from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from .models import User
from .schemas import UserCreate
from .security import get_password_hash
from fastapi import HTTPException

class UserCRUD:
    @staticmethod
    async def create_user(db: AsyncSession, user: UserCreate):
        try:
            hashed_password = get_password_hash(user.password)
            db_user = User(
                username=user.username, 
                email=user.email,
                hashed_password=hashed_password
            )
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)
            return db_user
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=400, detail="Username or email already exists")

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str):
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalars().first()