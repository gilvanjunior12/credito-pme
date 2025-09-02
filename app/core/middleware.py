import uuid
from starlette.middleware.base import BaseHTTPMiddleware

class TraceIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        tid = uuid.uuid4().hex[:12]
        request.state.trace_id = tid
        response = await call_next(request)
        response.headers["X-Trace-Id"] = tid
        return response

def add_middlewares(app):
    app.add_middleware(TraceIdMiddleware)
