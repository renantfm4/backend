from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from ...database.database import get_db
from ...database.schemas import UserCreate, UserUpdate, UserInviteSchema, UserCreateAdminSchema, AdminUserEdit, UserOut
from ...core.security import get_password_hash
from ...database import models
from ...crud.token import get_user_by_cpf, get_user, get_current_user
from ...core.hierarchy import require_role, RoleEnum

from ...core.security import generate_invite_token
from ...utils.send_email import send_invite_email


router = APIRouter()

# @router.post("/admin/convidar-usuario", response_model=UserInviteSchema)
# async def cadastrar_usuario(user_data: UserCreateAdminSchema, 
#                             background_tasks: BackgroundTasks,
#                             db: AsyncSession = Depends(get_db),
#                             current_user: models.User = Depends(require_role(RoleEnum.ADMIN))):
    
#     # Verifica se o CPF ou email já existem
#     stmt = select(models.User).filter((models.User.cpf == user_data.cpf) | (models.User.email == user_data.email))
#     result = await db.execute(stmt)
#     existing_user = result.scalars().first()
    
#     if existing_user:
#         raise HTTPException(status_code=400, detail="CPF ou Email já cadastrado")

#     # Verifica se Unidade de Saúde existe
#     stmt = select(models.UnidadeSaude).filter(models.UnidadeSaude.id == user_data.unidade_saude_id)
#     result = await db.execute(stmt)
#     unidade = result.scalars().first()
    
#     if not unidade:
#         raise HTTPException(status_code=404, detail="Unidade de Saúde não encontrada")

#     # Verifica se a Permissão existe
#     stmt = select(models.Role).filter(models.Role.id == user_data.role_id)
#     result = await db.execute(stmt)
#     role = result.scalars().first()
    
#     if not role:
#         raise HTTPException(status_code=404, detail="Permissão não encontrada")

#     # Criando usuário pendente
#     new_user = models.User(
#         email=user_data.email,
#         cpf=user_data.cpf,
#         fl_ativo=False, 
#         id_usuario_criacao = current_user.id
#     )
    
#     new_user.roles.append(role)
#     new_user.unidadeSaude.append(unidade)
    
#     db.add(new_user)
#     await db.commit()
#     await db.refresh(new_user)

#     # Gerar token de convite
#     invite_token = generate_invite_token(new_user.email)
#     invite_link = f"dermalert://register?token={invite_token}"
#     background_tasks.add_task(send_invite_email, new_user.email, invite_token)

#     return {"message": "Convite enviado com sucesso!"}

@router.post("/admin/convidar-usuario", response_model=UserInviteSchema)
async def cadastrar_usuario(
    user_data: UserCreateAdminSchema, 
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.ADMIN))
):
    
    # Verifica se o CPF ou email já existem
    stmt = select(models.User).filter(
        (models.User.cpf == user_data.cpf) | (models.User.email == user_data.email)
    )
    result = await db.execute(stmt)
    existing_user = result.scalars().first()
    
    # Verifica se Unidade de Saúde existe
    stmt = select(models.UnidadeSaude).filter(models.UnidadeSaude.id == user_data.unidade_saude_id)
    result = await db.execute(stmt)
    unidade = result.scalars().first()
    
    if not unidade:
        raise HTTPException(status_code=404, detail="Unidade de Saúde não encontrada")

    # Verifica se a Permissão existe
    stmt = select(models.Role).filter(models.Role.id == user_data.role_id)
    result = await db.execute(stmt)
    role = result.scalars().first()
    
    if not role:
        raise HTTPException(status_code=404, detail="Permissão não encontrada")

    # Caso de usuário existente
    if existing_user:
        # Verifica se o cadastro está incompleto (sem senha definida)
        if existing_user.senha_hash is None:
            # Verifica se o token anterior foi usado
            if existing_user.email_invite_token_used:
                # Gerar novo token de convite e atualizar no banco
                invite_token = generate_invite_token(existing_user.email)
                existing_user.email_invite_token = invite_token
                existing_user.email_invite_token_used = False
                existing_user.id_usuario_atualizacao = current_user.id
                
                # Enviar novo e-mail de convite
                invite_link = f"dermalert://register?token={invite_token}"
                background_tasks.add_task(send_invite_email, existing_user.email, invite_token)
                
                await db.commit()
                return {"message": "Novo convite enviado com sucesso para usuário com cadastro pendente!"}
            else:
                invite_token = generate_invite_token(existing_user.email)
                existing_user.email_invite_token = invite_token
                existing_user.email_invite_token_used = False
                existing_user.id_usuario_atualizacao = current_user.id
                invite_link = f"dermalert://register?token={invite_token}"
                background_tasks.add_task(send_invite_email, existing_user.email, invite_token)
                
                await db.commit()
                return {"message": "Convite reenviado com sucesso para usuário com cadastro pendente!"}
        else:
            # Usuário já completou o cadastro
            raise HTTPException(status_code=400, detail="CPF ou Email já cadastrado com registro completo")

    # Criando usuário pendente (caso novo)
    new_user = models.User(
        email=user_data.email,
        cpf=user_data.cpf,
        fl_ativo=False,
        id_usuario_criacao=current_user.id
    )
    
    new_user.roles.append(role)
    new_user.unidadeSaude.append(unidade)
    
    # Gerar token de convite e definir no usuário
    invite_token = generate_invite_token(new_user.email)
    new_user.email_invite_token = invite_token
    new_user.email_invite_token_used = False
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    # Enviar e-mail de convite
    invite_link = f"dermalert://register?token={invite_token}"
    background_tasks.add_task(send_invite_email, new_user.email, invite_token)

    return {"message": "Convite enviado com sucesso!"}

@router.post("/admin/editar-usuario", response_model=UserOut)
async def editar_usuario(user_data: AdminUserEdit, 
                         db: AsyncSession = Depends(get_db),
                         current_user: models.User = Depends(require_role(RoleEnum.ADMIN))):
    
    # editar unidade de saude e role de um usuario
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
    
    # Verifica se Unidade de Saúde existe
    stmt = select(models.UnidadeSaude).filter(models.UnidadeSaude.id == user_data.unidade_saude)
    result = await db.execute(stmt)
    unidade = result.scalars().first()

    if not unidade:
        raise HTTPException(status_code=404, detail="Unidade de Saúde não encontrada")
    
    # Verifica se a Permissão existe
    stmt = select(models.Role).filter(models.Role.id == user_data.role_id)
    result = await db.execute(stmt)
    role = result.scalars().first()

    if not role:
        raise HTTPException(status_code=404, detail="Permissão não encontrada")
    
    # Verifica se o usuário está tentando inativar a si mesmo
    if user.id == current_user.id and not user_data.fl_ativo:
        raise HTTPException(status_code=400, detail="Você não pode inativar a si mesmo")
    
    user.unidadeSaude = [unidade]
    user.roles = [role]
    user.fl_ativo = user_data.fl_ativo
    user.id_usuario_atualizacao = current_user.id

    await db.commit()
    await db.refresh(user)

    return user