from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import logging

logger = logging.getLogger("app")

def _trace_id(request: Request) -> str:
    return getattr(request.state, "trace_id", None) or "n/a"

def _collect_details(exc: RequestValidationError):
    details = []
    for err in exc.errors():
        details.append({
            "loc": list(err.get("loc", ())),
            "msg": err.get("msg", ""),
            "type": err.get("type", ""),
        })
    return details

async def validation_exception_handler(request: Request, exc: RequestValidationError):
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
    payload = {
        "error": {
            "code": "http_error",
            "message": exc.detail or "Erro HTTP",
            "trace_id": _trace_id(request),
        }
    }
    return JSONResponse(status_code=exc.status_code, content=payload)

async def unhandled_exception_handler(request: Request, exc: Exception):
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
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
