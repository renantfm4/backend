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
    fl_ativo: Optional[bool] = None

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
    fl_ativo: Optional[bool] = None


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
    fl_ativo: bool

    class Config:
        orm_mode = True

class UserOut(BaseModel):
    id: int
    nome_usuario: Optional[str] = None
    email: EmailStr
    cpf: str
    fl_ativo: bool
    roles: List[RoleOut] = []
    unidadeSaude: List[UnidadeSaudeOut] = []

    class Config:
        orm_mode = True

class UnidadeSaudeCreateSchema(BaseModel):
    nome_unidade_saude: str
    nome_localizacao: str
    codigo_unidade_saude: str
    cidade_unidade_saude: str
    fl_ativo: bool

class UnidadeSaudeUpdateSchema(BaseModel):
    nome_unidade_saude: Optional[str] = None
    nome_localizacao: Optional[str] = None
    codigo_unidade_saude: Optional[str] = None
    cidade_unidade_saude: Optional[str] = None
    fl_ativo: Optional[bool] = None

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
    arquivo_path: str

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


class GrauParentescoEnum(str, Enum):
    pai = "Pai"
    mae = "Mãe"
    avo = "Avô/Avó"
    irmao = "Irmão/Irmã"
    outro = "Outro"

class TipoCancerFamiliarEnum(str, Enum):
    melanoma = "Melanoma"
    carcinoma_basocelular = "Carcinoma Basocelular"
    carcinoma_espinocelular = "Carcinoma Espinocelular"
    outro = "Outro"

class TipoCancerPessoalEnum(str, Enum):
    melanoma = "Melanoma"
    carcinoma_basocelular = "Carcinoma Basocelular"
    carcinoma_espinocelular = "Carcinoma Espinocelular"
    outro = "Outro"

class TipoTratamentoEnum(str, Enum):
    cirurgia = "Cirurgia"
    crioterapia = "Crioterapia"
    radioterapia = "Radioterapia"
    outro = "Outro"

class FrequenciaExposicaoEnum(str, Enum):
    diariamente = "Diariamente"
    algumas_vezes_por_semana = "Algumas vezes por semana"
    ocasionalmente = "Ocasionalmente"

class QuantidadeQueimadurasEnum(str, Enum):
    um_dois = "1-2"
    tres_cinco = "3-5"
    mais_de_cinco = "Mais de 5"

class FatorProtecaoEnum(str, Enum):
    quinze = "15"
    trinta = "30"
    cinquenta = "50"
    setenta = "70"
    cem_ou_mais = "100 ou mais"

class FrequenciaCheckupsEnum(str, Enum):
    anualmente = "Anualmente"
    a_cada_seis_meses = "A cada 6 meses"
    outro = "Outro"

class TempoAlteracoesEnum(str, Enum):
    menos_de_um_mes = "Menos de 1 mês"
    um_tres_meses = "1-3 meses"
    tres_seis_meses = "3-6 meses"
    mais_de_seis_meses = "Mais de 6 meses"

class HistoricoCancerPeleCreateSchema(BaseModel):
    historico_familiar: bool = False
    grau_parentesco: Optional[GrauParentescoEnum] = None
    tipo_cancer_familiar: Optional[TipoCancerFamiliarEnum] = None
    tipo_cancer_familiar_outro: Optional[str] = None
    diagnostico_pessoal: bool = False
    tipo_cancer_pessoal: Optional[TipoCancerPessoalEnum] = None
    tipo_cancer_pessoal_outro: Optional[str] = None
    lesoes_precancerigenas: bool = False
    tratamento_lesoes: bool = False
    tipo_tratamento: Optional[TipoTratamentoEnum] = None
    tipo_tratamento_outro: Optional[str] = None

class FatoresRiscoProtecaoCreateSchema(BaseModel):
    exposicao_solar_prolongada: bool = False
    frequencia_exposicao_solar: Optional[FrequenciaExposicaoEnum] = None
    queimaduras_graves: bool = False
    quantidade_queimaduras: Optional[QuantidadeQueimadurasEnum] = None
    uso_protetor_solar: bool = False
    fator_protecao_solar: Optional[FatorProtecaoEnum] = None
    uso_chapeu_roupa_protecao: bool = False
    bronzeamento_artificial: bool = False
    checkups_dermatologicos: bool = False
    frequencia_checkups: Optional[FrequenciaCheckupsEnum] = None
    frequencia_checkups_outro: Optional[str] = None
    participacao_campanhas_prevencao: bool = False

class InvestigacaoLesoesSuspeitasCreateSchema(BaseModel):
    mudanca_pintas_manchas: bool = False
    sintomas_lesoes: bool = False
    tempo_alteracoes: Optional[TempoAlteracoesEnum] = None
    caracteristicas_lesoes: bool = False
    consulta_medica: bool = False
    diagnostico_lesoes: Optional[str] = None

class InformacoesCompletasCreateSchema(BaseModel):
    saude_geral: Optional[SaudeGeralCreateSchema] = None
    avaliacao_fototipo: Optional[AvaliacaoFototipoCreateSchema] = None
    historico_cancer_pele: Optional[HistoricoCancerPeleCreateSchema] = None
    fatores_risco_protecao: Optional[FatoresRiscoProtecaoCreateSchema] = None
    investigacao_lesoes_suspeitas: Optional[InvestigacaoLesoesSuspeitasCreateSchema] = None



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


class UserResponseSchema(BaseModel):
    id: int
    nome_usuario: str
    email: str
    cpf: str
    fl_ativo: bool
    nivel_acesso: Optional[int] = None 

    class Config:
        orm_mode = True