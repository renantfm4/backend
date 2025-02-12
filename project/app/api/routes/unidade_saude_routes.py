from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ...database.database import get_db
from ...core.hierarchy import require_role, RoleEnum
from ...database import models
from ...database.schemas import UnidadeSaudeCreateSchema, UnidadeSaudeUpdateSchema


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
        is_active=unidade_data.is_active
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
    
    update_data = unidade_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(unidade, field, value)
    
    await db.commit()
    await db.refresh(unidade)
    
    return unidade