from fastapi import APIRouter

from packages.animes import animes_router
from packages.auth import auth_router
from packages.episodes import episodes_router
from packages.franchises import franchises_router
from packages.users import users_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(users_router, prefix="/users", tags=["Users"])
router.include_router(animes_router, prefix="/animes", tags=["Animes"])
router.include_router(episodes_router, prefix="/episodes", tags=["Episodes"])
router.include_router(franchises_router, prefix="/franchises", tags=["Franchises"])
