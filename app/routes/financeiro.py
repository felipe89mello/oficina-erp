from datetime import datetime, date
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ContaReceber, ContaPagar, Pedido

router = APIRouter(prefix="/financeiro", tags=["financeiro"])
templates = Jinja2Templates(directory="app/templates")

_MESES_ABREV = [
    "jan", "fev", "mar", "abr", "mai", "jun",
    "jul", "ago", "set", "out", "nov", "dez",
]


def _parse_date(value: str):
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def _primeiro_dia_mes(d: date, meses_atras: int) -> date:
    total = (d.year * 12 + (d.month - 1)) - meses_atras
    ano, mes = divmod(total, 12)
    return date(ano, mes + 1, 1)


def _resumo_mensal(pedidos, contas_pagar, qtd_meses: int = 6):
    """Faturamento (pedidos do mês) x Despesas (contas pagas no mês),
    para os últimos `qtd_meses` meses, do mais antigo para o mais recente."""
    hoje = date.today()
    meses = [_primeiro_dia_mes(hoje, i) for i in range(qtd_meses - 1, -1, -1)]

    resumo = []
    for inicio_mes in meses:
        faturamento = sum(
            p.valor_total for p in pedidos
            if p.data_pedido.year == inicio_mes.year and p.data_pedido.month == inicio_mes.month
        )
        despesas = sum(
            c.valor for c in contas_pagar
            if c.status == "Pago" and c.data_pagamento
            and c.data_pagamento.year == inicio_mes.year and c.data_pagamento.month == inicio_mes.month
        )
        resumo.append({
            "label": f"{_MESES_ABREV[inicio_mes.month - 1]}/{str(inicio_mes.year)[2:]}",
            "faturamento": faturamento,
            "despesas": despesas,
            "liquido": faturamento - despesas,
        })
    return resumo


@router.get("")
def financeiro_index(request: Request, db: Session = Depends(get_db)):
    contas_receber = db.query(ContaReceber).order_by(ContaReceber.vencimento).all()
    contas_pagar = db.query(ContaPagar).order_by(ContaPagar.vencimento).all()
    pedidos = db.query(Pedido).all()

    total_a_receber = sum(c.valor for c in contas_receber if c.status == "Pendente")
    total_a_pagar = sum(c.valor for c in contas_pagar if c.status == "Pendente")

    resumo_mensal = _resumo_mensal(pedidos, contas_pagar)
    mes_atual = resumo_mensal[-1]
    maior_valor_grafico = max(
        [m["faturamento"] for m in resumo_mensal] + [m["despesas"] for m in resumo_mensal] + [1]
    )

    return templates.TemplateResponse(
        "financeiro/index.html",
        {
            "request": request,
            "contas_receber": contas_receber,
            "contas_pagar": contas_pagar,
            "total_a_receber": total_a_receber,
            "total_a_pagar": total_a_pagar,
            "saldo_previsto": total_a_receber - total_a_pagar,
            "faturamento_mes": mes_atual["faturamento"],
            "despesas_mes": mes_atual["despesas"],
            "liquido_mes": mes_atual["liquido"],
            "resumo_mensal": resumo_mensal,
            "maior_valor_grafico": maior_valor_grafico,
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
