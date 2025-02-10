from sqlalchemy import Column, Integer, String, ForeignKey, Table, JSON, TIMESTAMP, Boolean, Enum, DATE, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base
from .baseMixin import AuditMixin

# Association tables
user_roles = Table(
    'user_roles', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

user_unidadeSaude = Table(
    'user_unidadeSaude', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('unidadeSaude_id', Integer, ForeignKey('unidadeSaude.id'))
)

# Models
class User(AuditMixin, Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    nome_usuario = Column(String(50), unique=True, index=True, nullable=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    cpf = Column(String(11), unique=True, index=True, nullable=False)
    senha_hash = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=False)

    roles = relationship('Role', secondary=user_roles, back_populates='users')
    unidadeSaude = relationship('UnidadeSaude', secondary=user_unidadeSaude, back_populates='users')

class UnidadeSaude(Base):
    __tablename__ = 'unidadeSaude'
    id = Column(Integer, primary_key=True, index=True)
    nome_unidade_saude = Column(String(100), unique=True, index=True, nullable=False)
    nome_localizacao = Column(String(300), nullable=False)
    codigo_unidade_saude = Column(String(50), unique=True, index=True, nullable=False)
    cidade_unidade_saude = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True)
    users = relationship('User', secondary=user_unidadeSaude, back_populates='unidadeSaude')    

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    nivel_acesso = Column(Integer, nullable=False, default=1)
    users = relationship('User', secondary=user_roles, back_populates='roles')

class Atendimento(Base):
    __tablename__ = 'atendimentos'
    id = Column(Integer, primary_key=True, index=True)
    data_atendimento = Column(TIMESTAMP, server_default=func.now())

    paciente_id = Column(Integer, ForeignKey('pacientes.id'))
    paciente = relationship('Paciente')
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User')
    termo_consentimento_id = Column(Integer, ForeignKey('termoConsentimento.id'))
    termo_consentimento = relationship('TermoConsentimento')
    saude_geral_id = Column(Integer, ForeignKey('saudeGeral.id'))
    saude_geral = relationship('SaudeGeral')
    avaliacao_fototipo_id = Column(Integer, ForeignKey('avaliacao_fototipo.id'))
    avaliacao_fototipo = relationship('AvaliacaoFototipo')


class RegistroLesoes(Base):
    __tablename__ = 'registroLesoes'
    id = Column(Integer, primary_key=True, index=True)
    local_lesao = Column(String(100), nullable=False)
    descricao_lesao = Column(String(500), nullable=False)
    atendimento_id = Column(Integer, ForeignKey('atendimentos.id'))
    atendimento = relationship('Atendimento')


class RegistroLesoesImagens(Base):
    __tablename__ = 'registroLesoesImagens'
    id = Column(Integer, primary_key=True, index=True)
    arquivo_url = Column(String(300), nullable=False)
    registro_lesoes_id = Column(Integer, ForeignKey('registroLesoes.id'))
    registro_lesoes = relationship('RegistroLesoes')


class Paciente(Base):
    __tablename__ = 'pacientes'
    id = Column(Integer, primary_key=True, index=True)
    nome_paciente = Column(String(100), nullable=False)
    data_nascimento = Column(DATE, nullable=False)
    sexo = Column(Enum('M', 'F', 'NB', 'NR', 'O', name='sexo_enum'), nullable=False)
    sexo_outro = Column(String(100))
    cpf_paciente = Column(String(11), unique=True, index=True, nullable=False)
    num_cartao_sus = Column(String(15), unique=True, index=True, nullable=False)
    endereco_paciente = Column(String(300), nullable=False)
    telefone_paciente = Column(String(11), nullable=False)
    email_paciente = Column(String(100), nullable=False)
    autoriza_pesquisa = Column(Boolean, nullable=False)


class TermoConsentimento(Base):
    __tablename__ = 'termoConsentimento'
    id = Column(Integer, primary_key=True, index=True)
    arquivo_url = Column(String(300), nullable=False)
    data_acordo = Column(TIMESTAMP, server_default=func.now())

class SaudeGeral(Base):
    __tablename__ = 'saudeGeral'
    id = Column(Integer, primary_key=True, index=True)
    doencas_cronicas = Column(Boolean, nullable=False)
    hipertenso = Column(Boolean, nullable=False)
    diabetes = Column(Boolean, nullable=False)
    cardiopatia = Column(Boolean, nullable=False)
    outras_doencas = Column(String(300))
    diagnostico_cancer = Column(Boolean, nullable=False)
    tipo_cancer = Column(String(100))
    uso_medicamentos = Column(Boolean, nullable=False)
    medicamentos = Column(String(500))
    possui_alergia = Column(Boolean, nullable=False)
    alergias = Column(String(500))
    ciruturgias_dermatologicas = Column(Boolean, nullable=False)
    tipo_procedimento = Column(String(200))
    pratica_atividade_fisica = Column(Boolean, nullable=False)
    frequencia_atividade_fisica = Column(Enum('Diária', 'Frequente', 'Moderada', 'Ocasional', name='frequencia_atividade_fisica_enum'))

class AvaliacaoFototipo(Base):
    __tablename__ = 'avaliacao_fototipo'
    id = Column(Integer, primary_key=True, autoincrement=True)
    cor_pele = Column(Integer, nullable=False)
    cor_olhos = Column(Integer, nullable=False)
    cor_cabelo = Column(Integer, nullable=False)
    quantidade_sardas = Column(Integer, nullable=False)
    reacao_sol = Column(Integer, nullable=False)
    bronzeamento = Column(Integer, nullable=False)
    sensibilidade_solar = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint(cor_pele.in_([0, 2, 4, 8, 12, 16, 20]), name="check_cor_pele"),
        CheckConstraint(cor_olhos.in_([0, 1, 2, 3, 4]), name="check_cor_olhos"),
        CheckConstraint(cor_cabelo.in_([0, 1, 2, 3, 4]), name="check_cor_cabelo"),
        CheckConstraint(quantidade_sardas.in_([0, 1, 2, 3]), name="check_quantidade_sardas"),
        CheckConstraint(reacao_sol.in_([0, 2, 4, 6, 8]), name="check_reacao_sol"),
        CheckConstraint(bronzeamento.in_([0, 2, 4, 6]), name="check_bronzeamento"),
        CheckConstraint(sensibilidade_solar.in_([0, 1, 2, 3, 4]), name="check_sensibilidade_solar"),
    )



class AuditLog(Base):
    __tablename__ = 'audit_logs'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    change_type = Column(String(50))
    change_details = Column(JSON)
    changed_at = Column(TIMESTAMP, server_default=func.now())
    user = relationship('User')
