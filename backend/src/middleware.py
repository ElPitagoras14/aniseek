import time
import uuid
from typing import Callable

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from log import logger
from packages.auth import parse_jwt_data


class TracingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> JSONResponse:
        request_uuid = str(uuid.uuid4())

        auth_header = request.headers.get("Authorization")
        user = None

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]
            payload = parse_jwt_data(token)
            if payload:
                user = payload.get("id", None)

        request.state.uuid = request_uuid
        request.state.user = user

        start_time = time.perf_counter()

        with logger.contextualize(uuid=request_uuid, user=user or "anonymous"):
            if request.method != "OPTIONS":
                logger.info(f"{request.method} {request.url.path}")
            response = await call_next(request)

        duration = (time.perf_counter() - start_time) * 1000

        response.headers["X-Request-ID"] = request_uuid
        response.headers["X-Response-Time"] = f"{duration:.2f}ms"

        return response
