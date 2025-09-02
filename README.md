# Crédito PME API (FastAPI) 🚀

API para simular **score** e **limite sugerido** para pequenas e médias empresas (PME).

---

## 📑 Sumário
- [Como rodar](#-como-rodar)
- [Configuração (.env)](#-configuração-env)
- [Endpoints](#-endpoints)
- [Exemplos de requisição](#-exemplos-de-requisição)
- [Estrutura do projeto](#-estrutura-do-projeto)
- [Testes](#-testes)
- [Dicas (PyCharm)](#-dicas-pycharm)
- [Licença](#-licença)

---

## ✅ Como rodar

### Opção A — com 2 cliques (recomendada)

**Primeira vez (instalar dependências):**
```powershell
cd C:\Users\junin\credito-pme
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Depois (sempre): dê duplo clique em start.bat.

Acesse:

Swagger: http://127.0.0.1:8001/docs

Healthcheck: http://127.0.0.1:8001/healthz

### Opção B — manual (PowerShell)
```powershell
cd C:\Users\junin\credito-pme
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --port 8001
```

🔧 Configuração (.env)

O projeto lê variáveis via python-dotenv.

Exemplo (.env.example → .env):
```powershell
APP_NAME="Crédito PME API (DEV)"
```

🔗 Endpoints
```powershell
Método	                Rota	                          Descrição
GET	                  /healthz	                    Healthcheck simples
POST	                /v1/score	               Calcula score e limite_sugerido
POST	            /v1/score/motivos	          Mesmo cálculo + breakdown dos pontos
```

Request base (JSON)
```powershell
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
```

Response /v1/score (200)
```powershell
{
  "score": 640,
  "aprovado": true,
  "limite_sugerido": 9600
}
```

Response /v1/score/motivos (200)
```powershell
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
```
<details> <summary><b>Notas de cálculo</b></summary>

Base 300 + pontos por faturamento, tempo de atividade, inadimplência, nº de empregados e bônus por setor.
Score limitado a 0–1000.
Aprovado se ≥ 600.
Limite proporcional ao faturamento mensal.

</details>


🧪 Exemplos de requisição
PowerShell (Invoke-WebRequest)
```powershell
$body = '{"cnpj":"00.000.000/0001-00","faturamento_mensal":15000,"tempo_atividade_meses":18,"inadimplente":false,"setor":"Comercio","empregados":3}'
$r = Invoke-WebRequest -Method POST "http://127.0.0.1:8001/v1/score" -ContentType "application/json" -Body $body
$r.StatusCode
$r.Content
```

curl

(Windows PowerShell exige aspas escapadas):
```powershell
curl -X POST "http://127.0.0.1:8001/v1/score" -H "Content-Type: application/json" -d "{\"cnpj\":\"00.000.000/0001-00\",\"faturamento_mensal\":15000,\"tempo_atividade_meses\":18,\"inadimplente\":false,\"setor\":\"Comercio\",\"empregados\":3}"
```

🗂 Estrutura do projeto
```powershell
credito-pme/
├─ app/
│  ├─ api/
│  │  ├─ __init__.py
│  │  └─ routes.py           # Rotas /v1/score e /v1/score/motivos
│  ├─ core/
│  │  ├─ __init__.py
│  │  ├─ errors.py           # Handlers globais de erro + resposta padrão
│  │  └─ middleware.py       # CORS, Trace-ID, timing
│  ├─ models/
│  │  ├─ __init__.py
│  │  └─ schemas.py          # Pydantic (PedidoScore, ScoreResposta, etc.)
│  ├─ services/
│  │  ├─ __init__.py
│  │  └─ scoring.py          # Regras do score e motivos
│  └─ main.py                # Cria app e inclui rotas/middlewares
├─ tests/
│  └─ test_api.py            # 6 testes passando (pytest)
├─ .env.example
├─ .gitignore
├─ README.md
├─ requirements.txt
└─ start.bat
```

🧪 Testes
```powershell
cd C:\Users\junin\credito-pme
.\.venv\Scripts\Activate.ps1
pytest -q
```
Saída esperada:
```powershell
6 passed
```

💡 Dicas (PyCharm)

Run/Debug: crie uma configuração do tipo Python > Module name: uvicorn, parâmetros:
```powershell
app.main:app --reload --port 8001
```
Interpreter: use o da venv do projeto (.venv).

📄 Licença

Uso educacional.
