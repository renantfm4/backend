from pydantic import BaseModel, EmailStr
from typing import List, Optional

# class UserCreate(BaseModel):
#     username: str
#     email: str
#     password: str

# class RoleCreate(BaseModel):
#     name: str

# class PermissionCreate(BaseModel):
#     name: str
#     details: str

# class GroupCreate(BaseModel):
#     name: str



class UserBase(BaseModel):
    nome_usuario: str
    email: EmailStr
    cpf: str

class UserCreate(UserBase):
    senha: str

class UserUpdate(BaseModel):
    nome_usuario: Optional[str] = None
    email: Optional[EmailStr] = None
    cpf: Optional[str] = None
    senha: Optional[str] = None

class UserOut(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    refresh_token: str