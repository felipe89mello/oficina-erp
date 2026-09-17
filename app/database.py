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


def _coluna_existe(tabela: str, coluna: str) -> bool:
    with engine.connect() as conn:
        linhas = conn.exec_driver_sql(f"PRAGMA table_info({tabela})").fetchall()
    return any(linha[1] == coluna for linha in linhas)


def _adicionar_coluna_se_faltar(tabela: str, coluna: str, definicao_sql: str):
    """Migração leve: adiciona uma coluna a uma tabela já existente.

    create_all() só cria tabelas novas — ele nunca altera uma tabela que
    já existe no banco. Como não usamos uma ferramenta de migração (tipo
    Alembic) nesse projeto pequeno, qualquer coluna nova que adicionarmos
    no models.py precisa de uma linha aqui para chegar ao banco real do
    sogro sem perder os dados que já estão lá.
    """
    if not _coluna_existe(tabela, coluna):
        with engine.begin() as conn:
            conn.exec_driver_sql(f"ALTER TABLE {tabela} ADD COLUMN {definicao_sql}")


def init_db():
    # Importa os models aqui dentro para garantir que todas as tabelas
    # sejam registradas no Base antes do create_all.
    from app import models  # noqa: F401
    Base.metadata.create_all(bind=engine)

    # Migrações leves — cada linha cobre uma coluna nova adicionada
    # depois da versão inicial do banco. Rodar de novo não faz mal:
    # _adicionar_coluna_se_faltar já verifica se a coluna existe antes.
    _adicionar_coluna_se_faltar("pedidos", "descricao_servico", "descricao_servico TEXT")
