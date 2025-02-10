from pydantic import BaseModel, EmailStr
from typing import List, Optional

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

class AdminUserEdit(BaseModel):
    cpf: Optional[str] = None
    unidade_saude: Optional[int] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenRefresh(BaseModel):
    refresh_token: str

class UserInviteSchema(BaseModel):
    message: str

class UserCreateAdminSchema(BaseModel):
    cpf: str
    email: EmailStr
    unidade_saude_id: int
    role_id: int

class CompleteUserSchema(BaseModel):
    token: str
    nome_usuario: str
    senha: str

class UserCreateSupervisorSchema(BaseModel):
    email: EmailStr
    cpf: str
    role_id: int

class SupervisorUserEdit(BaseModel):
    cpf: Optional[str] = None
    role_id: Optional[int] = None
    is_active: Optional[bool] = None