# -----------------------------------------------------------------------------
# Objetivo: centralizar os handlers de exceção e devolver respostas JSON
# padronizadas (com trace_id) para facilitar debug e leitura pelo cliente.
# -----------------------------------------------------------------------------

from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

# Logger do app (configuração vem do main ou do runtime)
logger = logging.getLogger("app")

def _trace_id(request: Request) -> str:
    # Recupera o trace_id gerado pelo middleware; se não houver, usa "n/a".
    return getattr(request.state, "trace_id", None) or "n/a"

def _collect_details(exc: RequestValidationError):
    # Converte o objeto de validação em uma lista de dicts mais legíveis
    details = []
    for err in exc.errors():
        details.append({
            "loc": list(err.get("loc", ())),  # onde ocorreu o erro (corpo, campo, etc.)
            "msg": err.get("msg", ""),        # mensagem humana do erro
            "type": err.get("type", ""),      # tipo (value_error, type_error, etc.)
        })
    return details

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Handler para erros de validação do FastAPI (payload mal formatado, tipos, etc.)
    details = _collect_details(exc)
    msgs = [d["msg"] for d in details if d.get("msg")]
    base = "Erros de validação"
    human = base + (": " + "; ".join(msgs) if msgs else "")
    payload = {
        "error": {
            "code": "validation_error",
            "message": human,
            "details": details,
            "trace_id": _trace_id(request),
        }
    }
    logger.warning("422 validation_error %s %s", request.url.path, payload["error"]["trace_id"])
    return JSONResponse(status_code=422, content=payload)

async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # Handler para HTTPException (levantada pela própria stack Starlette/FastAPI)
    payload = {
        "error": {
            "code": "http_error",
            "message": exc.detail or "Erro HTTP",
            "trace_id": _trace_id(request),
        }
    }
    return JSONResponse(status_code=exc.status_code, content=payload)

async def unhandled_exception_handler(request: Request, exc: Exception):
    # Fallback para exceções não tratadas: logamos e retornamos 500 minimalista
    logger.exception("500 internal_error %s %s", request.url.path, _trace_id(request))
    payload = {
        "error": {
            "code": "internal_error",
            "message": "Erro interno",
            "trace_id": _trace_id(request),
        }
    }
    return JSONResponse(status_code=500, content=payload)

def register_exception_handlers(app: FastAPI) -> None:
    # Registra todos os handlers globais no app
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
