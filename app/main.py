import logging
from fastapi import FastAPI
from app.core.config import APP_NAME, API_VERSION
from app.api.routes import router as api_router
from app.core.errors import register_exception_handlers
from app.core.middleware import add_middlewares

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

app = FastAPI(title=APP_NAME, version=API_VERSION)

add_middlewares(app)
register_exception_handlers(app)

@app.get("/")
def root():
    return {"mensagem": "API de Crédito PME rodando!"}

@app.get("/healthz")
def healthz():
    return {"status": "ok"}

app.include_router(api_router)
