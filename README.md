# Sistema da Oficina

Sistema de gestão simples (pedidos, clientes e financeiro) desenvolvido
para uma oficina de costura artesanal e informal. Construído para rodar
100% local e offline em um notebook antigo (Windows 7), sem depender de
servidor, nuvem ou conexão com internet no dia a dia.

**Stack:** Python, FastAPI, SQLAlchemy, SQLite, Jinja2. Empacotado com
PyInstaller para rodar como aplicativo desktop (abre no navegador
padrão, sem instalação de dependências para o usuário final).

**Destaques técnicos:**
- Geração automática de contas a receber a partir de cada pedido
- Banco de dados isolado da pasta do app (`%APPDATA%`), permitindo
  atualizar o programa sem perder os dados do usuário
- Sem dependência de CDN/internet no frontend — necessário porque a
  máquina de destino roda majoritariamente offline
- Compatibilidade deliberada com Python 3.9 (última versão com suporte
  oficial ao Windows 7, sistema operacional da máquina de destino)

---

## Como rodar em desenvolvimento

```bash
python3.9 -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

pip install -r requirements.txt
python main.py
```

Isso sobe o servidor em `http://127.0.0.1:8000` e abre automaticamente
no navegador padrão.

## Estrutura

```
oficina-erp/
├── main.py                  # ponto de entrada (sobe servidor + abre navegador)
├── app/
│   ├── database.py          # config SQLite/SQLAlchemy
│   ├── models.py            # Cliente, Pedido, ContaReceber, ContaPagar
│   ├── routes/
│   │   ├── clientes.py
│   │   ├── pedidos.py       # criar pedido gera ContaReceber automaticamente
│   │   └── financeiro.py
│   ├── templates/           # Jinja2 (sem dependência de CDN/internet)
│   └── static/style.css
└── requirements.txt
```

## Empacotando para Windows 7 (.exe)

**Importante:** o Python 3.9 é a última versão com suporte oficial ao
Windows 7. Use Python 3.9 no ambiente onde for gerar o build.

Rode o build **diretamente no notebook de destino** (não no seu PC de
desenvolvimento), pra garantir compatibilidade total:

```bash
pip install pyinstaller
pyinstaller --onefile --add-data "app/templates;app/templates" --add-data "app/static;app/static" main.py
```

O executável final aparece em `dist/main.exe`.

### Antes de gerar o build final, ajustar:

1. Em `app/database.py`, trocar `DB_PATH` para uma pasta gravável do
   usuário (ex: `%APPDATA%\OficinaERP\oficina.db`), do mesmo jeito que
   foi feito no app-financeiro — evita perder dados a cada reinstalação.
2. Considerar backup automático do `.db` a cada abertura do app,
   seguindo o mesmo padrão (rotação das últimas N cópias + espelhamento
   opcional numa pasta sincronizada, ex: Google Drive).

## Próximos passos possíveis

- Parcelamento de Contas a Receber (sinal + restante) em vez de valor único
- Exportar relatório simples (PDF ou CSV) de pedidos do mês
- Tela de dashboard inicial com resumo (hoje redireciona direto para Pedidos)
