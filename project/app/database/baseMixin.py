from sqlalchemy import Column, TIMESTAMP, Boolean, Integer, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declared_attr

class AuditMixin:
    @declared_attr
    def data_criacao(cls):
        return Column(TIMESTAMP, server_default=func.now(), nullable=False)

    @declared_attr
    def data_atualizacao(cls):
        return Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), nullable=False)

    @declared_attr
    def id_usuario_criacao(cls):
        return Column(Integer, ForeignKey('users.id'), nullable=True)

    @declared_attr
    def id_usuario_atualizacao(cls):
        return Column(Integer, ForeignKey('users.id'), nullable=True)

    @declared_attr
    def fl_ativo(cls):
        return Column(Boolean, default=True, nullable=False)
