from fastapi import FastAPI

from app.api.routes.rag import router as rag_router


def create_application() -> FastAPI:
    app = FastAPI(
        title="RAG Service",
        version="1.0.0",
        description="Dedicated vector storage and retrieval service for Canvas AI workflows.",
    )
    app.include_router(rag_router)
    return app


app = create_application()
