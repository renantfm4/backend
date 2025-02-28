from pydantic import BaseModel, EmailStr
from fastapi import Form
from typing import List, Optional
from datetime import date

from enum import Enum

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

class UnidadeSaudeCreateSchema(BaseModel):
    nome_unidade_saude: str
    nome_localizacao: str
    codigo_unidade_saude: str
    cidade_unidade_saude: str
    is_active: bool

class UnidadeSaudeUpdateSchema(BaseModel):
    nome_unidade_saude: Optional[str] = None
    nome_localizacao: Optional[str] = None
    codigo_unidade_saude: Optional[str] = None
    cidade_unidade_saude: Optional[str] = None
    is_active: Optional[bool] = None

class sexoEnum(str, Enum):
    masculino = "M"
    feminino = "F"
    nao_binario = "NB"
    nao_respondeu = "NR"
    outro = "O"

class PacienteCreateSchema(BaseModel):
    nome_paciente: str
    data_nascimento: date
    sexo: sexoEnum = None
    sexo_outro: Optional[str] = None
    cpf_paciente: str
    num_cartao_sus: str
    endereco_paciente: str
    telefone_paciente: str
    email_paciente: str
    autoriza_pesquisa: bool

class TermoConsentimentoCreateSchema(BaseModel):
    arquivo_url: str

class FrequenciaAtividadeFisicaEnum(str, Enum):
    diaria = "Diária"
    frequente = "Frequente"
    moderada = "Moderada"
    ocasional = "Ocasional"

class SaudeGeralCreateSchema(BaseModel):
    doencas_cronicas: bool = False
    hipertenso: bool = False
    diabetes: bool = False
    cardiopatia: bool = False
    outras_doencas: Optional[str] = None
    diagnostico_cancer: bool = False
    tipo_cancer: Optional[str] = None
    uso_medicamentos: bool = False
    medicamentos: Optional[str] = None
    possui_alergia: bool = False
    alergias: Optional[str] = None
    ciruturgias_dermatologicas: bool = False
    tipo_procedimento: Optional[str] = None
    pratica_atividade_fisica: bool = False
    frequencia_atividade_fisica: Optional[FrequenciaAtividadeFisicaEnum] = None

class AvaliacaoFototipoCreateSchema(BaseModel):
    cor_pele: int
    cor_olhos: int
    cor_cabelo: int
    quantidade_sardas: int
    reacao_sol: int
    bronzeamento: int
    sensibilidade_solar: int

# class RegistroLesoesCreateSchema(BaseModel):
#     local_lesao: str
#     descricao_lesao: str

#     class Config:
#         orm_mode = True

class RegistroLesoesCreateSchema(BaseModel):
    local_lesao: str
    descricao_lesao: str

    @classmethod
    def as_form(
        cls,
        local_lesao: str = Form(...),
        descricao_lesao: str = Form(...)
    ):
        return cls(local_lesao=local_lesao, descricao_lesao=descricao_lesao)
    

class LocalLesaoSchema(BaseModel):
    id: int
    nome: str

    class Config:
        orm_mode = True
