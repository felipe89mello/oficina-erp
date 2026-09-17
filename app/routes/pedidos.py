from datetime import datetime, date
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Pedido, Cliente, ContaReceber

router = APIRouter(prefix="/pedidos", tags=["pedidos"])
templates = Jinja2Templates(directory="app/templates")


def _parse_date(value: str):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


@router.get("")
def listar_pedidos(request: Request, db: Session = Depends(get_db)):
    pedidos = db.query(Pedido).order_by(Pedido.data_pedido.desc()).all()
    return templates.TemplateResponse(
        "pedidos/list.html", {"request": request, "pedidos": pedidos, "active": "pedidos"}
    )


@router.get("/novo")
def novo_pedido_form(request: Request, db: Session = Depends(get_db)):
    clientes = db.query(Cliente).order_by(Cliente.nome).all()
    return templates.TemplateResponse(
        "pedidos/form.html",
        {"request": request, "pedido": None, "clientes": clientes, "active": "pedidos"},
    )


@router.post("/novo")
def criar_pedido(
    cliente_id: int = Form(...),
    descricao: str = Form(...),
    descricao_servico: str = Form(""),
    valor_total: float = Form(...),
    data_pedido: str = Form(...),
    prazo_entrega: str = Form(""),
    forma_pagamento: str = Form(""),
    db: Session = Depends(get_db),
):
    pedido = Pedido(
        cliente_id=cliente_id,
        descricao=descricao,
        descricao_servico=descricao_servico or None,
        valor_total=valor_total,
        data_pedido=_parse_date(data_pedido) or date.today(),
        prazo_entrega=_parse_date(prazo_entrega),
        forma_pagamento=forma_pagamento or None,
        status="Em andamento",
    )
    db.add(pedido)
    db.flush()  # garante pedido.id antes de criar a conta a receber

    conta = ContaReceber(
        pedido_id=pedido.id,
        descricao=f"Pedido #{pedido.id} - {descricao}",
        valor=valor_total,
        vencimento=pedido.prazo_entrega,
        status="Pendente",
    )
    db.add(conta)
    db.commit()
    return RedirectResponse(url="/pedidos", status_code=303)


@router.get("/{pedido_id}/editar")
def editar_pedido_form(pedido_id: int, request: Request, db: Session = Depends(get_db)):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    clientes = db.query(Cliente).order_by(Cliente.nome).all()
    return templates.TemplateResponse(
        "pedidos/form.html",
        {"request": request, "pedido": pedido, "clientes": clientes, "active": "pedidos"},
    )


@router.post("/{pedido_id}/editar")
def atualizar_pedido(
    pedido_id: int,
    cliente_id: int = Form(...),
    descricao: str = Form(...),
    descricao_servico: str = Form(""),
    valor_total: float = Form(...),
    data_pedido: str = Form(...),
    prazo_entrega: str = Form(""),
    forma_pagamento: str = Form(""),
    status: str = Form("Em andamento"),
    db: Session = Depends(get_db),
):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    pedido.cliente_id = cliente_id
    pedido.descricao = descricao
    pedido.descricao_servico = descricao_servico or None
    pedido.valor_total = valor_total
    pedido.data_pedido = _parse_date(data_pedido) or pedido.data_pedido
    pedido.prazo_entrega = _parse_date(prazo_entrega)
    pedido.forma_pagamento = forma_pagamento or None
    pedido.status = status
    db.commit()
    return RedirectResponse(url="/pedidos", status_code=303)


@router.post("/{pedido_id}/excluir")
def excluir_pedido(pedido_id: int, db: Session = Depends(get_db)):
    pedido = db.query(Pedido).filter(Pedido.id == pedido_id).first()
    if pedido:
        db.delete(pedido)
        db.commit()
    return RedirectResponse(url="/pedidos", status_code=303)
