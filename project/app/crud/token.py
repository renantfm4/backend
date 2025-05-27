from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from ..database.models import User
from ..core.security import verify_password
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from ..core.config import SECRET_KEY, ALGORITHM, oauth2_scheme
from fastapi import Depends, HTTPException, status
from ..database.database import get_db
from sqlalchemy.orm import selectinload


async def get_user_by_cpf(db: AsyncSession, cpf: str):
    result = await db.execute(
        select(User).options(selectinload(User.roles)).filter(User.cpf == cpf)
    )
    return result.scalars().first()


async def get_user(db: AsyncSession, user_id: int):
    result = await db.execute(select(User).filter(User.id == user_id))
    return result.scalars().first()


async def authenticate_user(db: AsyncSession, cpf: str, password: str):
    user = await get_user_by_cpf(db, cpf)
    if not user or not verify_password(password, user.senha_hash):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now() + (
        expires_delta if expires_delta else timedelta(minutes=15)
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Não foi possível validar as credenciais",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        cpf: str = payload.get("sub")
        if cpf is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # Consulta com eager loading para o relacionamento 'unidadeSaude'
    stmt = (
        select(User)
        .options(selectinload(User.unidadeSaude), selectinload(User.roles))
        .filter(User.cpf == cpf)
    )
    result = await db.execute(stmt)
    user = result.scalars().first()

    if user is None:
        raise credentials_exception
    return user
