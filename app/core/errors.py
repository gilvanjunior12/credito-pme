import logging
import uuid
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("app")

def _trace_id(request: Request) -> str:
    return getattr(request.state, "trace_id", uuid.uuid4().hex[:12])

def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        payload = {
            "error": {
                "code": "http_error",
                "message": exc.detail or "Erro HTTP",
                "status": exc.status_code,
                "trace_id": _trace_id(request),
            }
        }
        if exc.status_code == 404:
            payload["error"]["code"] = "not_found"
            if not exc.detail:
                payload["error"]["message"] = "Recurso não encontrado"
        return JSONResponse(status_code=exc.status_code, content=payload)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        details = [{"loc": list(e.get("loc", [])), "msg": e.get("msg"), "type": e.get("type")} for e in exc.errors()]
        payload = {
            "error": {
                "code": "validation_error",
                "message": "Erros de validação",
                "details": details,
                "trace_id": _trace_id(request),
            }
        }
        return JSONResponse(status_code=422, content=payload)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        tid = _trace_id(request)
        logger.exception("Unhandled error [%s]", tid)
        payload = {"error": {"code": "internal_error", "message": "Erro interno. Tente novamente.", "trace_id": tid}}
        return JSONResponse(status_code=500, content=payload)
