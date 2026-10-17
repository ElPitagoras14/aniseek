from loguru import logger

from database.client import engine

from . import repository
from .schemas import McpSettingsUpdateInfo, SettingsUpdateInfo


async def get_settings_controller() -> dict:
    async with engine.connect() as conn:
        settings = await repository.get_settings(conn)
    return {
        "registration_policy": settings["registration_policy"],
        "mcp_enabled": settings["mcp_enabled"],
    }


async def get_mcp_settings_controller() -> dict:
    async with engine.connect() as conn:
        enabled = await repository.is_mcp_enabled(conn)
    return {"enabled": enabled}


async def update_settings_controller(info: SettingsUpdateInfo, user_id: str) -> dict:
    async with engine.begin() as conn:
        await repository.update_registration_policy(
            conn, info.registration_policy, user_id
        )
    logger.info(f"Registration policy set to {info.registration_policy} by {user_id}")
    return await get_settings_controller()


async def update_mcp_settings_controller(
    info: McpSettingsUpdateInfo, user_id: str
) -> dict:
    async with engine.begin() as conn:
        await repository.update_mcp_enabled(conn, info.enabled, user_id)
    logger.info(f"MCP {'enabled' if info.enabled else 'disabled'} by {user_id}")
    return await get_settings_controller()
