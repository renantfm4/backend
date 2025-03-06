from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from ...database.database import get_db
# from ...crud.user import create_user, assign_role_to_user, assign_permission_to_user, assign_user_to_group
from ...database.schemas import UserCreate, UserUpdate, UserInviteSchema, UserCreateSupervisorSchema, AdminUserEdit, SupervisorUserEdit, UserOut
from ...core.security import get_password_hash
from ...database import models
from ...crud.token import get_user_by_cpf, get_user, get_current_user
from ...core.hierarchy import require_role, RoleEnum

from ...core.security import generate_invite_token
from ...utils.send_email import send_invite_email

router = APIRouter()

@router.post("/supervisor/convidar-usuario", response_model=UserInviteSchema)
async def cadastrar_usuario_supervisor(
    user_data: UserCreateSupervisorSchema, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.SUPERVISOR))
):
    # Verifica se o CPF ou email já estão cadastrados
    stmt = select(models.User).filter(
        (models.User.cpf == user_data.cpf) | (models.User.email == user_data.email)
    )
    result = await db.execute(stmt)
    existing_user = result.scalars().first()
    
    if existing_user:
        raise HTTPException(status_code=400, detail="CPF ou Email já cadastrado")
    
    # Obter a Unidade de Saúde do supervisor logado
    # Aqui estamos assumindo que current_user.unidadeSaude é uma lista com a(s) unidade(s)
    if not current_user.unidadeSaude:
        raise HTTPException(status_code=400, detail="Supervisor não possui Unidade de Saúde definida")
    
    # Considerando que o supervisor está vinculado a apenas uma Unidade de Saúde
    unidade = current_user.unidadeSaude[0]

    # Verifica se a Permissão (role) existe
    stmt = select(models.Role).filter(models.Role.id == user_data.role_id)
    result = await db.execute(stmt)
    role = result.scalars().first()
    
    if not role:
        raise HTTPException(status_code=404, detail="Permissão não encontrada")
    
    # Apenas roles com nível <= SUPERVISOR são permitidas (ou seja, SUPERVISOR e PESQUISADOR)
    if role.nivel_acesso > RoleEnum.SUPERVISOR:
        raise HTTPException(
            status_code=400, 
            detail="Permissão não permitida para supervisores"
        )
        
    # Criação do usuário pendente
    new_user = models.User(
        email=user_data.email,
        cpf=user_data.cpf,
        fl_ativo=False, 
        id_usuario_criacao=current_user.id
    )
    
    # Associa a role e a unidade de saúde
    new_user.roles.append(role)
    new_user.unidadeSaude.append(unidade)
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    # Gerar token de convite e enviar e-mail
    invite_token = generate_invite_token(new_user.email)
    invite_link = f"sitebonito.com/completar-cadastro?token={invite_token}"
    background_tasks.add_task(send_invite_email, new_user.email, invite_link)
    
    return {"message": "Convite enviado com sucesso!"}


@router.post("/supervisor/editar-usuario", response_model=UserOut)
async def editar_usuario_supervisor(
    user_data: SupervisorUserEdit,  # Schema contendo: cpf, role_id e fl_ativo
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.SUPERVISOR))
):
    # Busca o usuário a ser editado pelo CPF
    # stmt = select(models.User).filter(models.User.cpf == user_data.cpf)
    stmt = (
        select(models.User)
        .options(
            selectinload(models.User.unidadeSaude),
            selectinload(models.User.roles)
            )
        .filter(models.User.cpf == user_data.cpf)
    )
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Opcional: verifique se o usuário pertence à mesma Unidade de Saúde do supervisor
    # Assumindo que cada usuário possui pelo menos uma Unidade de Saúde e que o supervisor possui uma única unidade vinculada.
    if not current_user.unidadeSaude:
        raise HTTPException(status_code=400, detail="Supervisor não possui Unidade de Saúde definida")
    if not user.unidadeSaude:
        raise HTTPException(status_code=400, detail="Usuário não possui Unidade de Saúde definida")
    
    supervisor_unidade = current_user.unidadeSaude[0].id
    # Caso o usuário esteja associado a múltiplas unidades, verifique se a unidade do supervisor consta entre elas
    if supervisor_unidade not in [unidade.id for unidade in user.unidadeSaude]:
        raise HTTPException(
            status_code=403, 
            detail="Você não tem permissão para editar esse usuário, pois ele não pertence à sua Unidade de Saúde"
        )
    
    # Busca a role informada
    stmt = select(models.Role).filter(models.Role.id == user_data.role_id)
    result = await db.execute(stmt)
    role = result.scalars().first()

    if not role:
        raise HTTPException(status_code=404, detail="Permissão não encontrada")
    
    # Garante que a role escolhida seja de nível SUPERVISOR ou inferior
    if role.nivel_acesso > RoleEnum.SUPERVISOR:
        raise HTTPException(
            status_code=400, 
            detail="Você não pode atribuir uma permissão maior do que SUPERVISOR"
        )
    
    user.roles = [role]
    user.fl_ativo = user_data.fl_ativo
    user.id_usuario_atualizacao = current_user.id

    await db.commit()
    await db.refresh(user)

    return user