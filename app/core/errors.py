from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

def _to_jsonable(obj):
    try:
        import json
        json.dumps(obj)
        return obj
    except Exception:
        if isinstance(obj, list):
            return [_to_jsonable(x) for x in obj]
        if isinstance(obj, dict):
            return {k: _to_jsonable(v) for k, v in obj.items()}
        return str(obj)

def _extract_field_names(exc: RequestValidationError) -> str:
    try:
        errs = exc.errors()
    except Exception:
        return ""
    fields = []
    for e in errs:
        loc = e.get("loc", [])
        for part in loc:
            if isinstance(part, str) and part not in ("body",):
                fields.append(part)
    # nomes únicos mantendo ordem
    seen = set()
    uniq = []
    for f in fields:
        if f not in seen:
            seen.add(f)
            uniq.append(f)
    return " / ".join(uniq)

# 422 - validação
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    fields = _extract_field_names(exc)
    # Incluo também a string do erro (vem do ValueError do validator) -> contém 'faturamento'
    raw_msg = str(exc)
    base_msg = "Erro de validação nos dados de entrada."
    if fields:
        base_msg = f"{base_msg} Verifique os campos: {fields}."
    if raw_msg:
        base_msg = f"{base_msg} Detalhe: {raw_msg}"

    details = _to_jsonable(getattr(exc, "errors", lambda: [])())
    return JSONResponse(
        status_code=422,
        content={"error": {"code": "validation_error", "message": base_msg, "details": details}},
    )

# Demais HTTP
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": "http_error", "message": getattr(exc, "detail", "Erro HTTP.")}},
    )

def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
