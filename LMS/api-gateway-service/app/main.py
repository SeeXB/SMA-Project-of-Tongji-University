from fastapi import FastAPI

from app.api.routes.gateway import router as gateway_router
from app.core.config import settings


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.gateway_title,
        version=settings.gateway_version,
        description=(
            "Unified entry point for the Canvas AI-enhanced subsystem. "
            "The gateway keeps a single public port while preserving "
            "independent internal microservices."
        ),
    )
    app.include_router(gateway_router)
    return app


app = create_application()
