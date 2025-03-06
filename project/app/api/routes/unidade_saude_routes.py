from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from ...database.database import get_db
from ...core.hierarchy import require_role, RoleEnum
from ...database import models
from ...database.schemas import UnidadeSaudeCreateSchema, UnidadeSaudeUpdateSchema, UserResponseSchema


router = APIRouter()

@router.post("/cadastrar-unidade-saude")
async def cadastrar_unidade_saude(
    unidade_data: UnidadeSaudeCreateSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.ADMIN))
):
    # Verifica se a Unidade de Saúde já existe
    stmt = select(models.UnidadeSaude).filter(models.UnidadeSaude.codigo_unidade_saude == unidade_data.codigo_unidade_saude)
    result = await db.execute(stmt)
    existing_unidade = result.scalars().first()
    
    if existing_unidade:
        raise HTTPException(status_code=400, detail="Unidade de Saúde já cadastrada")
    
    new_unidade = models.UnidadeSaude(
        nome_unidade_saude=unidade_data.nome_unidade_saude,
        nome_localizacao=unidade_data.nome_localizacao,
        codigo_unidade_saude=unidade_data.codigo_unidade_saude,
        cidade_unidade_saude=unidade_data.cidade_unidade_saude,
        fl_ativo=unidade_data.fl_ativo,
        id_usuario_criacao = current_user.id
    )
    
    db.add(new_unidade)
    await db.commit()
    await db.refresh(new_unidade)
    
    return new_unidade

@router.get("/listar-unidades-saude")
async def listar_unidades_saude(db: AsyncSession = Depends(get_db)):
    stmt = select(models.UnidadeSaude)
    result = await db.execute(stmt)
    unidades = result.scalars().all()
    
    return unidades

@router.get("/listar-unidade-saude/{unidade_id}")
async def listar_unidade_saude(unidade_id: int, db: AsyncSession = Depends(get_db)):
    stmt = select(models.UnidadeSaude).filter(models.UnidadeSaude.id == unidade_id)
    result = await db.execute(stmt)
    unidade = result.scalars().first()
    
    if not unidade:
        raise HTTPException(status_code=404, detail="Unidade de Saúde não encontrada")
    
    return unidade

@router.post("/editar-unidade-saude/{unidade_id}")
async def editar_unidade_saude(
    unidade_id: int, 
    unidade_data: UnidadeSaudeUpdateSchema, 
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.ADMIN))
):
    stmt = select(models.UnidadeSaude).filter(models.UnidadeSaude.id == unidade_id)
    result = await db.execute(stmt)
    unidade = result.scalars().first()
    
    if not unidade:
        raise HTTPException(status_code=404, detail="Unidade de Saúde não encontrada")
    
    update_data = unidade_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(unidade, field, value)
    
    unidade.id_usuario_atualizacao = current_user.id
    
    await db.commit()
    await db.refresh(unidade)
    
    return unidade

@router.get("/listar-usuarios-unidade-saude/{unidade_id}", response_model=List[UserResponseSchema])
async def listar_usuarios_unidade_saude(
    unidade_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role(RoleEnum.SUPERVISOR))
):
    stmt = select(models.UnidadeSaude).filter(models.UnidadeSaude.id == unidade_id).options(
        selectinload(models.UnidadeSaude.users)
        .selectinload(models.User.roles)
    )
    result = await db.execute(stmt)
    unidade = result.scalars().first()
    
    if not unidade:
        raise HTTPException(status_code=404, detail="Unidade de Saúde não encontrada")
    
    users_with_nivel = []
    for user in unidade.users:
        if not user.senha_hash or not user.nome_usuario:
            continue

        nivel_acesso = max([role.nivel_acesso for role in user.roles]) if user.roles else None

        user_dict = {
            "id": user.id,
            "nome_usuario": user.nome_usuario,
            "email": user.email,
            "cpf": user.cpf,
            "fl_ativo": user.fl_ativo,
            "nivel_acesso": nivel_acesso
        }
        users_with_nivel.append(user_dict)
    
    return users_with_nivel