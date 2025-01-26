from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from .database import get_async_session
from .crud import UserCRUD
from .schemas import UserCreate, UserResponse
from .security import create_access_token, verify_password
from .config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Advanced FastAPI Project",
    version="0.1.0"
)

@app.post("/users/", response_model=UserResponse)
async def create_user(
    user: UserCreate, 
    db: AsyncSession = Depends(get_async_session)
):
    return await UserCRUD.create_user(db, user)

@app.post("/token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_session)
):
    user = await UserCRUD.get_user_by_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}