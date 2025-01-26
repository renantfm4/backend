from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from ...database.database import get_db
from ...crud.user import create_user, assign_role_to_user, assign_permission_to_user, assign_user_to_group
from ...database.schemas import UserCreate

router = APIRouter()

@router.post("/users/")
async def create_user_route(user: UserCreate, db: AsyncSession = Depends(get_db)):
    """
    Rota para criar um novo usuário.
    """
    try:
        return await create_user(db, user)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/users/{user_id}/roles/{role_id}")
async def assign_role_to_user_route(user_id: int, role_id: int, db: AsyncSession = Depends(get_db)):
    """
    Rota para atribuir uma função a um usuário.
    """
    try:
        return await assign_role_to_user(db, user_id, role_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/users/{user_id}/permissions/{permission_id}")
async def assign_permission_to_user_route(user_id: int, permission_id: int, db: AsyncSession = Depends(get_db)):
    """
    Rota para atribuir uma permissão a um usuário.
    """
    try:
        return await assign_permission_to_user(db, user_id, permission_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/users/{user_id}/groups/{group_id}")
async def assign_user_to_group_route(user_id: int, group_id: int, db: AsyncSession = Depends(get_db)):
    """
    Rota para atribuir um usuário a um grupo.
    """
    try:
        return await assign_user_to_group(db, user_id, group_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    
