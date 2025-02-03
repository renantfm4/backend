# from sqlalchemy.ext.asyncio import AsyncSession
# from ..database.models import Permission
# from ..database.schemas import PermissionCreate

# async def create_permission(db: AsyncSession, permission: PermissionCreate):
#     db_permission = Permission(name=permission.name, details=permission.details)
#     db.add(db_permission)
#     await db.commit()
#     await db.refresh(db_permission)
#     return db_permission