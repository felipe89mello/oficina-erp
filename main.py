"""
Sistema da Oficina — ponto de entrada.

Ao rodar este arquivo:
1. Garante que o banco SQLite existe (cria as tabelas se necessário).
2. Sobe o servidor FastAPI localmente (127.0.0.1:8000).
3. Abre o navegador padrão apontando para o sistema, como uma aba normal.

Uso em desenvolvimento:
    python main.py

Depois de empacotado com PyInstaller, o .exe final faz exatamente a
mesma coisa — sem precisar de terminal ou instalação de navegador
específico, já que usa o navegador padrão do Windows.
"""
import threading
import webbrowser

import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from app.database import init_db
from app.routes import clientes, pedidos, financeiro

HOST = "127.0.0.1"
PORT = 8000

app = FastAPI(title="Sistema da Oficina")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(clientes.router)
app.include_router(pedidos.router)
app.include_router(financeiro.router)


@app.get("/")
def home():
    return RedirectResponse(url="/pedidos")


def _abrir_navegador():
    webbrowser.open(f"http://{HOST}:{PORT}")


if __name__ == "__main__":
    init_db()
    # Abre o navegador 1.5s depois de iniciar, dando tempo do servidor subir
    threading.Timer(1.5, _abrir_navegador).start()
    uvicorn.run(app, host=HOST, port=PORT, log_level="warning")
