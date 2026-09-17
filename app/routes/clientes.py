from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Cliente, Pedido

router = APIRouter(prefix="/clientes", tags=["clientes"])
templates = Jinja2Templates(directory="app/templates")


@router.get("")
def listar_clientes(request: Request, db: Session = Depends(get_db)):
    clientes = db.query(Cliente).order_by(Cliente.nome).all()
    return templates.TemplateResponse(
        "clientes/list.html", {"request": request, "clientes": clientes, "active": "clientes"}
    )


@router.get("/novo")
def novo_cliente_form(request: Request):
    return templates.TemplateResponse(
        "clientes/form.html", {"request": request, "cliente": None, "active": "clientes"}
    )


@router.post("/novo")
def criar_cliente(
    nome: str = Form(...),
    telefone: str = Form(""),
    endereco: str = Form(""),
    db: Session = Depends(get_db),
):
    cliente = Cliente(nome=nome, telefone=telefone or None, endereco=endereco or None)
    db.add(cliente)
    db.commit()
    return RedirectResponse(url="/clientes", status_code=303)


@router.get("/{cliente_id}")
def detalhe_cliente(cliente_id: int, request: Request, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    pedidos = (
        db.query(Pedido)
        .filter(Pedido.cliente_id == cliente_id)
        .order_by(Pedido.data_pedido.desc())
        .all()
    )
    return templates.TemplateResponse(
        "clientes/detail.html",
        {"request": request, "cliente": cliente, "pedidos": pedidos, "active": "clientes"},
    )


@router.get("/{cliente_id}/editar")
def editar_cliente_form(cliente_id: int, request: Request, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    return templates.TemplateResponse(
        "clientes/form.html", {"request": request, "cliente": cliente, "active": "clientes"}
    )


@router.post("/{cliente_id}/editar")
def atualizar_cliente(
    cliente_id: int,
    nome: str = Form(...),
    telefone: str = Form(""),
    endereco: str = Form(""),
    db: Session = Depends(get_db),
):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    cliente.nome = nome
    cliente.telefone = telefone or None
    cliente.endereco = endereco or None
    db.commit()
    return RedirectResponse(url="/clientes", status_code=303)


@router.post("/{cliente_id}/excluir")
def excluir_cliente(cliente_id: int, db: Session = Depends(get_db)):
    cliente = db.query(Cliente).filter(Cliente.id == cliente_id).first()
    if cliente:
        db.delete(cliente)
        db.commit()
    return RedirectResponse(url="/clientes", status_code=303)
