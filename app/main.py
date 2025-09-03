# -----------------------------------------------------------------------------
# Cria a aplicação FastAPI, configura middlewares, handlers de erro
# e expõe os endpoints principais.
# -----------------------------------------------------------------------------

import logging
from fastapi import FastAPI
from app.core.config import APP_NAME, API_VERSION
from app.api.routes import router as api_router
from app.core.errors import register_exception_handlers
from app.core.middleware import add_middlewares

# Configuração de logging padrão (envia logs para o console)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

# Instância principal do FastAPI
app = FastAPI(title=APP_NAME, version=API_VERSION)

# Ativa middlewares (ex.: trace-id)
add_middlewares(app)

# Registra handlers de erro globais
register_exception_handlers(app)

@app.get("/")
def root():
    # Endpoint raiz: usado como mensagem de boas-vindas
    return {"mensagem": "API de Crédito PME rodando!"}

@app.get("/healthz")
def healthz():
    # Healthcheck simples para monitoramento
    return {"status": "ok"}

# Inclui as rotas da API (score, motivos, etc.)
app.include_router(api_router)
