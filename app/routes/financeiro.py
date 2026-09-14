from datetime import datetime, date
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ContaReceber, ContaPagar

router = APIRouter(prefix="/financeiro", tags=["financeiro"])
templates = Jinja2Templates(directory="app/templates")


def _parse_date(value: str):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


@router.get("")
def financeiro_index(request: Request, db: Session = Depends(get_db)):
    contas_receber = db.query(ContaReceber).order_by(ContaReceber.vencimento).all()
    contas_pagar = db.query(ContaPagar).order_by(ContaPagar.vencimento).all()

    total_a_receber = sum(c.valor for c in contas_receber if c.status == "Pendente")
    total_a_pagar = sum(c.valor for c in contas_pagar if c.status == "Pendente")

    return templates.TemplateResponse(
        "financeiro/index.html",
        {
            "request": request,
            "contas_receber": contas_receber,
            "contas_pagar": contas_pagar,
            "total_a_receber": total_a_receber,
            "total_a_pagar": total_a_pagar,
            "saldo_previsto": total_a_receber - total_a_pagar,
            "active": "financeiro",
        },
    )


@router.post("/receber/{conta_id}/marcar")
def marcar_recebido(conta_id: int, db: Session = Depends(get_db)):
    conta = db.query(ContaReceber).filter(ContaReceber.id == conta_id).first()
    if conta:
        conta.status = "Recebido" if conta.status == "Pendente" else "Pendente"
        conta.data_recebimento = date.today() if conta.status == "Recebido" else None
        db.commit()
    return RedirectResponse(url="/financeiro", status_code=303)


@router.post("/pagar/novo")
def criar_conta_pagar(
    descricao: str = Form(...),
    valor: float = Form(...),
    vencimento: str = Form(""),
    categoria: str = Form(""),
    db: Session = Depends(get_db),
):
    conta = ContaPagar(
        descricao=descricao,
        valor=valor,
        vencimento=_parse_date(vencimento),
        categoria=categoria or None,
        status="Pendente",
    )
    db.add(conta)
    db.commit()
    return RedirectResponse(url="/financeiro", status_code=303)


@router.post("/pagar/{conta_id}/marcar")
def marcar_pago(conta_id: int, db: Session = Depends(get_db)):
    conta = db.query(ContaPagar).filter(ContaPagar.id == conta_id).first()
    if conta:
        conta.status = "Pago" if conta.status == "Pendente" else "Pendente"
        conta.data_pagamento = date.today() if conta.status == "Pago" else None
        db.commit()
    return RedirectResponse(url="/financeiro", status_code=303)


@router.post("/pagar/{conta_id}/excluir")
def excluir_conta_pagar(conta_id: int, db: Session = Depends(get_db)):
    conta = db.query(ContaPagar).filter(ContaPagar.id == conta_id).first()
    if conta:
        db.delete(conta)
        db.commit()
    return RedirectResponse(url="/financeiro", status_code=303)
