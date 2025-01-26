from sqlalchemy.ext.asyncio import AsyncSession
from ..database.models import User, Role, Permission, Group
from ..database.schemas import UserCreate
from ..core.security import get_password_hash
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select

async def create_user(db: AsyncSession, user: UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, password_hash=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def assign_role_to_user(db: AsyncSession, user_id: int, role_id: int):
    result = await db.execute(select(User).filter(User.id == user_id).options(selectinload(User.roles)))
    user = result.scalar_one_or_none()

    result = await db.execute(select(Role).filter(Role.id == role_id))
    role = result.scalar_one_or_none()

    
    if not user or not role:
        raise ValueError("User or Role not found")
    
    # Assign role
    user.roles.append(role)
    
    # Commit changes
    await db.commit()
    await db.refresh(user)
     
    return user

async def assign_permission_to_user(db: AsyncSession, user_id: int, permission_id: int):
    # user = await db.get(User, user_id)
    # permission = await db.get(Permission, permission_id)

    result = await db.execute(select(User).filter(User.id == user_id).options(selectinload(User.permissions)))
    user = result.scalar_one_or_none()

    result = await db.execute(select(Permission).filter(Permission.id == permission_id))
    permission = result.scalar_one_or_none()
    
    if not user or not permission:
        raise ValueError("User or Permission not found")
    
    # Assign permission
    user.permissions.append(permission)
    
    # Commit changes
    await db.commit()
    await db.refresh(user)
    
    return user

async def assign_user_to_group(db: AsyncSession, user_id: int, group_id: int):
    # user = await db.get(User, user_id)
    # group = await db.get(Group, group_id)

    result = await db.execute(select(User).filter(User.id == user_id).options(selectinload(User.groups)))
    user = result.scalar_one_or_none()

    result = await db.execute(select(Group).filter(Group.id == group_id))
    group = result.scalar_one_or_none()
    
    if not user or not group:
        raise ValueError("User or Group not found")
    
    # Assign user to group
    user.groups.append(group)
    
    # Commit changes
    await db.commit()
    await db.refresh(user)
    
    return user