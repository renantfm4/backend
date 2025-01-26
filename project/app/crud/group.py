from sqlalchemy.ext.asyncio import AsyncSession
from ..database.models import Group
from ..database.schemas import GroupCreate

async def create_group(db: AsyncSession, group: GroupCreate):
    db_group = Group(name=group.name)
    db.add(db_group)
    await db.commit()
    await db.refresh(db_group)
    return db_group

