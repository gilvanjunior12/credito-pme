from fastapi import FastAPI
from app.core.config import APP_NAME, API_VERSION
from app.api.routes import router as api_router

app = FastAPI(title=APP_NAME, version=API_VERSION)

@app.get("/")
def root():
    return {"mensagem": "API de Crédito PME rodando!"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

app.include_router(api_router)
