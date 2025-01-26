from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..database.models import Role, Permission
from ..database.schemas import RoleCreate
from sqlalchemy.orm import selectinload

async def create_role(db: AsyncSession, role: RoleCreate):
    db_role = Role(name=role.name)
    db.add(db_role)
    await db.commit()
    await db.refresh(db_role)
    return db_role

async def assign_permission_to_role(
    role_id: int,
    permission_id: int,
    db: AsyncSession
) -> dict:
    # Load role with permissions
    role_stmt = select(Role).options(selectinload(Role.permissions)).where(Role.id == role_id)
    result = await db.execute(role_stmt)
    role = result.scalar_one_or_none()

    # Get permission
    perm_stmt = select(Permission).where(Permission.id == permission_id)
    result = await db.execute(perm_stmt)
    permission = result.scalar_one_or_none()

    # Validate existence
    if not role or not permission:
        raise HTTPException(
            status_code=404,
            detail="Role or Permission not found"
        )

    # Assign permission
    role.permissions.append(permission)
    await db.commit()

    return {"message": "Permission assigned to role"}