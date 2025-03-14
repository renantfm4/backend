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
    nome_usuario = Column(String(50), index=True, nullable=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    cpf = Column(String(11), unique=True, index=True, nullable=False)
    senha_hash = Column(String(255), nullable=True)
    # is_active = Column(Boolean, default=False)
    password_reset_token = Column(String(255), nullable=True)
    password_reset_token_used = Column(Boolean, default=False)

    roles = relationship('Role', secondary=user_roles, back_populates='users')
    unidadeSaude = relationship('UnidadeSaude', secondary=user_unidadeSaude, back_populates='users')

class UnidadeSaude(AuditMixin, Base):
    __tablename__ = 'unidadeSaude'
    id = Column(Integer, primary_key=True, index=True)
    nome_unidade_saude = Column(String(100), index=True, nullable=False)
    nome_localizacao = Column(String(300), nullable=False)
    codigo_unidade_saude = Column(String(50), unique=True, index=True, nullable=False)
    cidade_unidade_saude = Column(String(100), nullable=False)
    # is_active = Column(Boolean, default=True)
    users = relationship('User', secondary=user_unidadeSaude, back_populates='unidadeSaude')    

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    nivel_acesso = Column(Integer, nullable=False, default=1)
    users = relationship('User', secondary=user_roles, back_populates='roles')

class Atendimento(AuditMixin, Base):
    __tablename__ = 'atendimentos'
    id = Column(Integer, primary_key=True, index=True)
    data_atendimento = Column(TIMESTAMP, server_default=func.now())

    paciente_id = Column(Integer, ForeignKey('pacientes.id'))
    paciente = relationship('Paciente')
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', foreign_keys=[user_id])
    termo_consentimento_id = Column(Integer, ForeignKey('termoConsentimento.id'))
    termo_consentimento = relationship('TermoConsentimento')
    saude_geral_id = Column(Integer, ForeignKey('saudeGeral.id'))
    saude_geral = relationship('SaudeGeral')
    avaliacao_fototipo_id = Column(Integer, ForeignKey('avaliacao_fototipo.id'))
    avaliacao_fototipo = relationship('AvaliacaoFototipo')
    historico_cancer_pele_id = Column(Integer, ForeignKey('historicoCancerPele.id'))
    historico_cancer_pele = relationship('HistoricoCancerPele')
    fatores_risco_protecao_id = Column(Integer, ForeignKey('fatoresRiscoProtecao.id'))
    fatores_risco_protecao = relationship('FatoresRiscoProtecao')
    investigacao_lesoes_suspeitas_id = Column(Integer, ForeignKey('investigacaoLesoesSuspeitas.id'))
    investigacao_lesoes_suspeitas = relationship('InvestigacaoLesoesSuspeitas')
    
    
    unidade_saude_id = Column(Integer, ForeignKey('unidadeSaude.id'))
    unidade_saude = relationship('UnidadeSaude')


class RegistroLesoes(Base):
    __tablename__ = 'registroLesoes'
    id = Column(Integer, primary_key=True, index=True)
    # local_lesao = Column(String(100), nullable=False)
    local_lesao_id = Column(Integer, ForeignKey('locais_lesao.id'), nullable=False)
    descricao_lesao = Column(String(500), nullable=False)
    atendimento_id = Column(Integer, ForeignKey('atendimentos.id'))

    atendimento = relationship('Atendimento')
    local_lesao = relationship('LocalLesao')


class RegistroLesoesImagens(Base):
    __tablename__ = 'registroLesoesImagens'
    id = Column(Integer, primary_key=True, index=True)
    arquivo_url = Column(String(400), nullable=False)
    registro_lesoes_id = Column(Integer, ForeignKey('registroLesoes.id'))
    registro_lesoes = relationship('RegistroLesoes')

class LocalLesao(Base):
    __tablename__ = 'locais_lesao'
    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(100), unique=True, nullable=False)

class Paciente(AuditMixin, Base):
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
    arquivo_url = Column(String(400), nullable=False)
    data_acordo = Column(TIMESTAMP, server_default=func.now())

class SaudeGeral(Base):
    __tablename__ = 'saudeGeral'
    id = Column(Integer, primary_key=True, index=True)
    doencas_cronicas = Column(Boolean, nullable=False, default=False)
    hipertenso = Column(Boolean, nullable=False, default=False)
    diabetes = Column(Boolean, nullable=False, default=False)
    cardiopatia = Column(Boolean, nullable=False, default=False)
    outras_doencas = Column(String(300))
    diagnostico_cancer = Column(Boolean, nullable=False, default=False)
    tipo_cancer = Column(String(100))
    uso_medicamentos = Column(Boolean, nullable=False, default=False)
    medicamentos = Column(String(500))
    possui_alergia = Column(Boolean, nullable=False, default=False)
    alergias = Column(String(500))
    ciruturgias_dermatologicas = Column(Boolean, nullable=False, default=False)
    tipo_procedimento = Column(String(200))
    pratica_atividade_fisica = Column(Boolean, nullable=False, default=False)
    frequencia_atividade_fisica = Column(Enum('Diária', 'Frequente', 'Moderada', 'Ocasional', name='frequencia_atividade_fisica_enum'), default=None)

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


class HistoricoCancerPele(Base):
    __tablename__ = 'historicoCancerPele'
    id = Column(Integer, primary_key=True, autoincrement=True)
    historico_familiar = Column(Boolean, nullable=False, default=False)
    grau_parentesco = Column(Enum('Pai', 'Mãe', 'Avô/Avó', 'Irmão/Irmã', 'Outro', name='grau_parentesco_enum'), nullable=True)
    tipo_cancer_familiar = Column(Enum('Melanoma', 'Carcinoma Basocelular', 'Carcinoma Espinocelular', 'Outro', name='tipo_cancer_familiar_enum'), nullable=True)
    tipo_cancer_familiar_outro = Column(String(100), nullable=True)
    
    diagnostico_pessoal = Column(Boolean, nullable=False, default=False)
    tipo_cancer_pessoal = Column(Enum('Melanoma', 'Carcinoma Basocelular', 'Carcinoma Espinocelular', 'Outro', name='tipo_cancer_pessoal_enum'), nullable=True)
    tipo_cancer_pessoal_outro = Column(String(100), nullable=True)
    
    lesoes_precancerigenas = Column(Boolean, nullable=False, default=False)
    tratamento_lesoes = Column(Boolean, nullable=False, default=False)
    tipo_tratamento = Column(Enum('Cirurgia', 'Crioterapia', 'Radioterapia', 'Outro', name='tipo_tratamento_enum'), nullable=True)
    tipo_tratamento_outro = Column(String(100), nullable=True)


class FatoresRiscoProtecao(Base):
    __tablename__ = 'fatoresRiscoProtecao'
    id = Column(Integer, primary_key=True, autoincrement=True)
    exposicao_solar_prolongada = Column(Boolean, nullable=False, default=False)
    frequencia_exposicao_solar = Column(Enum('Diariamente', 'Algumas vezes por semana', 'Ocasionalmente', name='frequencia_exposicao_enum'), nullable=True)
    
    queimaduras_graves = Column(Boolean, nullable=False, default=False)
    quantidade_queimaduras = Column(Enum('1-2', '3-5', 'Mais de 5', name='quantidade_queimaduras_enum'), nullable=True)
    
    uso_protetor_solar = Column(Boolean, nullable=False, default=False)
    fator_protecao_solar = Column(Enum('15', '30', '50', '70', '100 ou mais', name='fator_protecao_enum'), nullable=True)
    
    uso_chapeu_roupa_protecao = Column(Boolean, nullable=False, default=False)
    
    bronzeamento_artificial = Column(Boolean, nullable=False, default=False)
    
    checkups_dermatologicos = Column(Boolean, nullable=False, default=False)
    frequencia_checkups = Column(Enum('Anualmente', 'A cada 6 meses', 'Outro', name='frequencia_checkups_enum'), nullable=True)
    frequencia_checkups_outro = Column(String(100), nullable=True)
    
    participacao_campanhas_prevencao = Column(Boolean, nullable=False, default=False)


class InvestigacaoLesoesSuspeitas(Base):
    __tablename__ = 'investigacaoLesoesSuspeitas'
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    mudanca_pintas_manchas = Column(Boolean, nullable=False, default=False)
    sintomas_lesoes = Column(Boolean, nullable=False, default=False)
    
    tempo_alteracoes = Column(Enum('Menos de 1 mês', '1-3 meses', '3-6 meses', 'Mais de 6 meses', name='tempo_alteracoes_enum'), nullable=True)
    
    caracteristicas_lesoes = Column(Boolean, nullable=False, default=False)
    
    consulta_medica = Column(Boolean, nullable=False, default=False)
    diagnostico_lesoes = Column(String(300), nullable=True)
