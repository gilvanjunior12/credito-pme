# Crédito PME API (FastAPI)

API simples para simular **score** e **limite sugerido** para pequenas e médias empresas.

## Rodando localmente

```bash
# criar e ativar venv (Windows PowerShell)
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

# subir a API
uvicorn app.main:app --reload --port 8001
