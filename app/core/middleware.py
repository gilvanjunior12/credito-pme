# -----------------------------------------------------------------------------
# Objetivo: adicionar middlewares transversais.
# - TraceIdMiddleware: injeta um X-Trace-Id por request, útil para correlação de logs.
# - add_middlewares: ponto único para registrar os middlewares no app.
# -----------------------------------------------------------------------------

import uuid
from starlette.middleware.base import BaseHTTPMiddleware

class TraceIdMiddleware(BaseHTTPMiddleware):
    # Gera um identificador curto por request e expõe no response header.
    async def dispatch(self, request, call_next):
        tid = uuid.uuid4().hex[:12]      # 12 chars: suficiente p/ rastrear sem poluir
        request.state.trace_id = tid     # deixa disponível para handlers/erros
        response = await call_next(request)
        response.headers["X-Trace-Id"] = tid  # cliente consegue ver o mesmo id
        return response

def add_middlewares(app):
    # Ponto único para habilitar os middlewares da aplicação
    app.add_middleware(TraceIdMiddleware)
