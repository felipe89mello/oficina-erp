"""
Configuração do banco de dados SQLite.

O arquivo do banco fica em um único lugar (DB_PATH). Quando o app for
empacotado com PyInstaller, ajustamos esse caminho para uma pasta
gravável do usuário (ex: %APPDATA%\\OficinaERP), seguindo o mesmo
padrão usado no app-financeiro.
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# O banco fica em uma pasta gravável do usuário (fora da pasta do app),
# assim atualizar o programa (trocar o .exe) nunca sobrescreve os dados.
APPDATA_DIR = os.path.join(os.getenv("APPDATA", os.path.expanduser("~")), "OficinaERP")
os.makedirs(APPDATA_DIR, exist_ok=True)
DB_PATH = os.path.join(APPDATA_DIR, "oficina.db")

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    # Importa os models aqui dentro para garantir que todas as tabelas
    # sejam registradas no Base antes do create_all.
    from app import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
