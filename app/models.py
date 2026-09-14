from datetime import date
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    telefone = Column(String, nullable=True)
    endereco = Column(String, nullable=True)

    pedidos = relationship("Pedido", back_populates="cliente", cascade="all, delete-orphan")


class Pedido(Base):
    __tablename__ = "pedidos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    descricao = Column(String, nullable=False)
    valor_total = Column(Float, nullable=False, default=0)
    data_pedido = Column(Date, nullable=False, default=date.today)
    prazo_entrega = Column(Date, nullable=True)
    status = Column(String, nullable=False, default="Em andamento")  # Em andamento / Concluído / Entregue
    forma_pagamento = Column(String, nullable=True)

    cliente = relationship("Cliente", back_populates="pedidos")
    contas_receber = relationship("ContaReceber", back_populates="pedido", cascade="all, delete-orphan")


class ContaReceber(Base):
    __tablename__ = "contas_receber"

    id = Column(Integer, primary_key=True, index=True)
    pedido_id = Column(Integer, ForeignKey("pedidos.id"), nullable=False)
    descricao = Column(String, nullable=False)
    valor = Column(Float, nullable=False, default=0)
    vencimento = Column(Date, nullable=True)
    status = Column(String, nullable=False, default="Pendente")  # Pendente / Recebido
    data_recebimento = Column(Date, nullable=True)

    pedido = relationship("Pedido", back_populates="contas_receber")


class ContaPagar(Base):
    __tablename__ = "contas_pagar"

    id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String, nullable=False)
    valor = Column(Float, nullable=False, default=0)
    vencimento = Column(Date, nullable=True)
    status = Column(String, nullable=False, default="Pendente")  # Pendente / Pago
    data_pagamento = Column(Date, nullable=True)
    categoria = Column(String, nullable=True)  # tecido / aviamento / luz / outros
