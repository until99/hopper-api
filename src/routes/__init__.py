from fastapi import APIRouter
from src.controllers import (
    auth_router,
    user_router,
    group_router,
    powerbi_router,
    pipeline_router,
)


def setup_routes(app):
    """Configura todas as rotas da aplicação."""
    api_router = APIRouter()

    # Inclui todos os routers
    api_router.include_router(auth_router)
    api_router.include_router(user_router)
    api_router.include_router(group_router)
    api_router.include_router(powerbi_router)
    api_router.include_router(pipeline_router)

    # Adiciona o router principal à aplicação
    app.include_router(api_router)
