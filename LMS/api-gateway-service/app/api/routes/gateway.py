from fastapi import APIRouter, HTTPException, Request, Response

from app.services.proxy_service import proxy_service

router = APIRouter()


@router.get("/health")
async def health() -> dict:
    return {
        "service": "api-gateway-service",
        "status": "UP",
        "routes": [
            "/course",
            "/assignment",
            "/qa",
            "/moderation",
            "/ai",
            "/rag",
        ],
    }


@router.api_route(
    "/{full_path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"],
)
async def proxy(full_path: str, request: Request) -> Response:
    try:
        return await proxy_service.forward(request, full_path)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"No upstream service for path: /{full_path}") from exc
