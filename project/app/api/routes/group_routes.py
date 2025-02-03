# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.ext.asyncio import AsyncSession  
# from ...database.database import get_db
# from ...crud.group import create_group
# from ...database.schemas import GroupCreate

# router = APIRouter()

# @router.post("/group", response_model=GroupCreate)
# async def create_group_route(group: GroupCreate, db: AsyncSession = Depends(get_db)):
#     return await create_group(db, group)