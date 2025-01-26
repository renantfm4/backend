from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession 
from ...database.database import get_db
from ...crud.role import create_role, assign_permission_to_role
from ...database.schemas import RoleCreate

router = APIRouter()

@router.post("/roles/")
async def create_role_route(role: RoleCreate, db: AsyncSession = Depends(get_db)):
    """
    Rota para criar uma nova função.
    """
    try:
        return await create_role(db, role)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/roles/{role_id}/permissions/{permission_id}")
async def assign_permission_to_role_route(role_id: int, permission_id: int, db: AsyncSession = Depends(get_db)):
    """
    Rota para atribuir uma permissão a uma função.
    """
    try:
        return await assign_permission_to_role(role_id, permission_id, db)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))