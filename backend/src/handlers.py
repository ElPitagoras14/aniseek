from fastapi import Request
from fastapi.responses import JSONResponse

from exceptions import AppError
from log import logger
from responses import camelize


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    payload = exc.payload
    if payload is not None:
        payload = camelize(payload)

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status_code": exc.status_code,
            "status": "error",
            "code": exc.code,
            "message": exc.message,
            "payload": payload,
        },
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(f"Unhandled error: {exc} - Path: {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={
            "status": "error",
            "message": "Internal server error",
            "payload": None,
        },
    )
