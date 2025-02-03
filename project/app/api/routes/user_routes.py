from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ...database.database import get_db
# from ...crud.user import create_user, assign_role_to_user, assign_permission_to_user, assign_user_to_group
from ...database.schemas import UserCreate, UserOut, UserUpdate
from ...core.security import get_password_hash
from ...database import models
from ...crud.token import get_user_by_cpf, get_user, get_current_user


router = APIRouter()

@router.post("/users/", response_model=UserOut)
def create_user(user: UserCreate, 
                db: AsyncSession = Depends(get_db),
                current_user: models.User = Depends(get_current_user)
):
    db_user = get_user_by_cpf(db, cpf=user.cpf)
    if db_user:
        raise HTTPException(status_code=400, detail="CPF já cadastrado")
    hashed_password = get_password_hash(user.senha)
    new_user = models.User(
        nome_usuario=user.nome_usuario,
        cpf=user.cpf,
        email=user.email,
        senha_hash=hashed_password
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/users/", response_model=List[UserOut])
async def read_users(
    skip: int = 0, 
    limit: int = 100, 
    db: AsyncSession = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    result = await db.execute(select(models.User).offset(skip).limit(limit))
    users = result.scalars().all()
    return users

@router.get("/users/{cpf}", response_model=UserOut)
async def read_user(
    cpf: str, 
    db: AsyncSession = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    result = await db.execute(select(models.User).filter(models.User.cpf == cpf))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

@router.put("/users/{cpf}", response_model=UserOut)
async def update_user(
    cpf: str, 
    user_update: UserUpdate, 
    db: AsyncSession = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    user = await get_user(db, cpf)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    if user_update.nome_usuario is not None:
        user.nome_usuario = user_update.nome_usuario
    if user_update.cpf is not None:
        user.cpf = user_update.cpf
    if user_update.email is not None:
        user.email = user_update.email
    if user_update.senha is not None:
        user.senha_hash = get_password_hash(user_update.senha)
    
    await db.commit()
    await db.refresh(user)
    return user

async def delete_user(
    cpf: str, 
    db: AsyncSession = Depends(get_db), 
    current_user: models.User = Depends(get_current_user)
):
    user = await get_user(db, cpf)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    db.delete(user)
    await db.commit()
    return

# @router.post("/users/")
# async def create_user_route(user: UserCreate, db: AsyncSession = Depends(get_db)):
#     """
#     Rota para criar um novo usuário.
#     """
#     try:
#         return await create_user(db, user)
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
    
# @router.post("/users/{user_id}/roles/{role_id}")
# async def assign_role_to_user_route(user_id: int, role_id: int, db: AsyncSession = Depends(get_db)):
#     """
#     Rota para atribuir uma função a um usuário.
#     """
#     try:
#         return await assign_role_to_user(db, user_id, role_id)
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
    
# @router.post("/users/{user_id}/permissions/{permission_id}")
# async def assign_permission_to_user_route(user_id: int, permission_id: int, db: AsyncSession = Depends(get_db)):
#     """
#     Rota para atribuir uma permissão a um usuário.
#     """
#     try:
#         return await assign_permission_to_user(db, user_id, permission_id)
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
    
# @router.post("/users/{user_id}/groups/{group_id}")
# async def assign_user_to_group_route(user_id: int, group_id: int, db: AsyncSession = Depends(get_db)):
#     """
#     Rota para atribuir um usuário a um grupo.
#     """
#     try:
#         return await assign_user_to_group(db, user_id, group_id)
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=str(e))
    
    
