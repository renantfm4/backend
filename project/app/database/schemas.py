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


class RoleOut(BaseModel):
    id: int
    name: str
    nivel_acesso: int

    class Config:
        orm_mode = True

class UnidadeSaudeOut(BaseModel):
    id: int
    nome_unidade_saude: str
    nome_localizacao: str
    codigo_unidade_saude: str
    cidade_unidade_saude: str
    is_active: bool

    class Config:
        orm_mode = True

class UserOut(BaseModel):
    id: int
    nome_usuario: Optional[str] = None
    email: EmailStr
    cpf: str
    is_active: bool
    roles: List[RoleOut] = []
    unidadeSaude: List[UnidadeSaudeOut] = []

    class Config:
        orm_mode = True