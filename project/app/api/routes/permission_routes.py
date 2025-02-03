# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.ext.asyncio import AsyncSession 
# from ...database.database import get_db
# from ...crud.permission import create_permission
# from ...database.schemas import PermissionCreate

# router = APIRouter()

# @router.post("/permission", response_model=PermissionCreate)
# async def create_permission_route(permission: PermissionCreate, db: AsyncSession = Depends(get_db)):
#     return await create_permission(db, permission)
