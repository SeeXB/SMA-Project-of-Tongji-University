from fastapi import FastAPI

from app.api.routes.inference import router as inference_router


def create_application() -> FastAPI:
    app = FastAPI(
        title="AI Gateway Service",
        version="1.0.0",
        description="Unified synchronous inference entry point for Canvas AI capabilities.",
    )
    app.include_router(inference_router)
    return app


app = create_application()
