Crédito PME API (FastAPI)

API para simular score e limite sugerido para pequenas e médias empresas.

Requisitos

Python 3.12+ (Windows)

PowerShell

Como rodar
Opção A — com 2 cliques (recomendado)

Primeira vez (instalar dependências):

cd C:\Users\junin\credito-pme
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt


Depois: dê duplo clique em start.bat.

Acesse:

Swagger (Docs): http://127.0.0.1:8001/docs

Redoc: http://127.0.0.1:8001/redoc

Healthcheck: http://127.0.0.1:8001/healthz

Opção B — manual pelo PowerShell
cd C:\Users\junin\credito-pme
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8001

Configuração (.env)

O projeto lê variáveis de ambiente via python-dotenv.

Exemplo de .env (você pode copiar de .env.example):

APP_NAME="Crédito PME API (DEV)"

Endpoints
POST /v1/score

Calcula score e limite_sugerido.

Request (JSON):

{
  "cnpj": "00.000.000/0001-00",
  "faturamento_mensal": 15000,
  "tempo_atividade_meses": 18,
  "inadimplente": false,
  "setor": "Comercio",
  "empregados": 3
}


Também aceita faturamento_anual (em vez de faturamento_mensal) e
meses_operando (em vez de tempo_atividade_meses).

Response (200):

{
  "score": 640,
  "aprovado": true,
  "limite_sugerido": 9600
}

POST /v1/score/motivos

Mesma entrada do /v1/score, mas retorna também o detalhamento dos pontos.

Response (200):

{
  "score": 640,
  "aprovado": true,
  "limite_sugerido": 9600,
  "breakdown": [
    {"fator": "faturamento", "pontos": 150, "motivo": "+150 por faturamento..."},
    {"fator": "tempo_atividade", "pontos": 18, "motivo": "+18 por 18 meses..."},
    {"fator": "inadimplencia", "pontos": 50, "motivo": "+50 sem inadimplência"},
    {"fator": "empregados", "pontos": 10, "motivo": "+10 por 3 empregados..."},
    {"fator": "setor", "pontos": 10, "motivo": "+10 para setor 'Comercio'"}
  ]
}

Teste rápido por linha de comando (opcional)

PowerShell:

$body = '{"cnpj":"00.000.000/0001-00","faturamento_mensal":15000,"tempo_atividade_meses":18,"inadimplente":false,"setor":"Comercio","empregados":3}'
Invoke-WebRequest -Method POST "http://127.0.0.1:8001/v1/score" -ContentType "application/json" -Body $body | Select-Object StatusCode,Content


curl:

curl -X POST "http://127.0.0.1:8001/v1/score" ^
  -H "Content-Type: application/json" ^
  -d "{\"cnpj\":\"00.000.000/0001-00\",\"faturamento_mensal\":15000,\"tempo_atividade_meses\":18,\"inadimplente\":false,\"setor\":\"Comercio\",\"empregados\":3}"

Executar os testes
cd C:\Users\junin\credito-pme
.\.venv\Scripts\Activate.ps1
pytest -q

Estrutura do projeto
credito-pme/
├─ app/
│  ├─ main.py
│  ├─ api/
│  │  ├─ __init__.py
│  │  └─ routes.py
│  ├─ core/
│  │  ├─ __init__.py
│  │  ├─ errors.py
│  │  └─ middleware.py
│  ├─ models/
│  │  ├─ __init__.py
│  │  └─ schemas.py
│  └─ services/
│     ├─ __init__.py
│     └─ scoring.py
├─ tests/
│  └─ test_api.py
├─ .env.example
├─ .gitignore
├─ README.md
├─ requirements.txt
├─ pytest.ini
└─ start.bat

Observações

CORS liberado para * (útil para um front local).

X-Trace-Id é adicionado em cada resposta para rastreio.

Erros de validação retornam JSON padronizado.

Licença

Uso educacional.