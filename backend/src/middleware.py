import time
from fastapi import Request
import uuid
from jose import JWTError, jwt
from loguru import logger
from config import general_settings

SECRET_KEY = general_settings.SECRET_KEY
ALGORITHM = general_settings.ALGORITHM


async def add_logging_and_timing(request: Request, call_next):
    request_id = str(uuid.uuid4())
    request.state.request_id = request_id

    username = None
    token = request.headers.get("authorization")
    if token:
        token = token.split(" ")[-1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username = payload.get("username")
        except JWTError:
            username = None

    start_time = time.time()

    with logger.contextualize(request_id=request_id, username=username):
        response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = request_id
    request.state.process_time = process_time

    return response
