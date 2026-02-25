from fastapi import Request
from fastapi.responses import JSONResponse
from .exceptions import CustomHTTPException
from .responses import APIResponse


async def custom_http_exception_handler(
    request: Request, exc: CustomHTTPException
):
    response_data = APIResponse(
        success=False,
        message=exc.detail,
        func=getattr(request.state, "func", "unknown"),
        error_code=exc.status_code,
    )

    # Headers con metadata
    headers = {
        "X-Request-ID": exc.request_id or request.state.request_id,
        "X-Process-Time": str(getattr(request.state, "process_time", 0)),
        "X-Func": getattr(request.state, "func", "unknown"),
    }

    return JSONResponse(
        status_code=exc.status_code,
        content=response_data.model_dump(exclude_none=True),
        headers=headers,
    )


async def general_exception_handler(request: Request, exc: Exception):
    response_data = APIResponse(
        success=False,
        message="Internal server error",
        func=getattr(request.state, "func", "unknown"),
        error_code=500,
    )

    # Headers con metadata
    headers = {
        "X-Request-ID": request.state.request_id,
        "X-Process-Time": str(getattr(request.state, "process_time", 0)),
        "X-Func": getattr(request.state, "func", "unknown"),
    }

    return JSONResponse(
        status_code=500,
        content=response_data.model_dump(exclude_none=True),
        headers=headers,
    )
