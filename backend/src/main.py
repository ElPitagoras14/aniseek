from contextlib import asynccontextmanager

from fastapi.responses import JSONResponse
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from database import connect_db, disconnect_db
from exceptions import AppError
from handlers import app_error_handler, unhandled_error_handler
from log import configure_logs
from middleware import TracingMiddleware
from packages.auth import get_hash, get_user_id_by_username, insert_user
from packages.auth.config import auth_settings
from routes import router
from config import Environment, general_settings


ENVIRONMENT = general_settings.ENVIRONMENT

configure_logs()


async def _seed_admin_user():
    existing = await get_user_id_by_username(auth_settings.ADMIN_USER)
    if existing:
        logger.info(f"Admin user '{auth_settings.ADMIN_USER}' already exists")
        return
    hashed = get_hash(auth_settings.ADMIN_PASS)
    await insert_user(auth_settings.ADMIN_USER, hashed, role_id=1)
    logger.info(f"Seeded admin user '{auth_settings.ADMIN_USER}' (role admin)")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    if not auth_settings.AUTH_ENABLED:
        await _seed_admin_user()
    logger.info("Application starting up...")
    yield
    await disconnect_db()
    logger.info("Application shutting down...")


app = FastAPI(
    title="AniSeek API",
    description="API for scraped anime data from various sources.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TracingMiddleware)

app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, unhandled_error_handler)

app.include_router(router, prefix="/api")


@app.get("/api/health")
async def health_check():
    return JSONResponse(
        status_code=200,
        content={
            "status": "ok",
            "environment": ENVIRONMENT.value,
        },
    )


def start():
    logger.info(
        f"Starting AniSeek API server in {ENVIRONMENT.value} mode on port {8000}"
    )
    is_dev = ENVIRONMENT == Environment.dev
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=8000,
        reload=is_dev,
        access_log=False,
    )


if __name__ == "__main__":
    start()
