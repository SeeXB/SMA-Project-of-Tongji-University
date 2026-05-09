from typing import Dict

import httpx
from fastapi import Request, Response

from app.core.config import settings


class ProxyService:
    # Keep routing rules in one service so the HTTP layer stays thin and
    # future gateway concerns like auth/rate limiting can evolve independently.
    def __init__(self) -> None:
        self._routes: Dict[str, str] = {
            "/course": settings.course_service_url,
            "/assignment": settings.assignment_service_url,
            "/qa": settings.qa_service_url,
            "/moderation": settings.moderation_service_url,
            "/ai": settings.ai_gateway_service_url,
            "/rag": settings.rag_service_url,
            "/actuator": settings.course_service_url,
            "/swagger-ui": settings.course_service_url,
            "/v3/api-docs": settings.course_service_url,
        }

    def resolve_backend(self, path: str) -> str:
        for prefix, backend in self._routes.items():
            if path == prefix or path.startswith(prefix + "/"):
                return backend
        raise KeyError(path)

    async def forward(self, request: Request, full_path: str) -> Response:
        path = "/" + full_path.lstrip("/")
        backend = self.resolve_backend(path)
        target_url = f"{backend}{path}"

        filtered_headers = {
            key: value
            for key, value in request.headers.items()
            if key.lower() not in {"host", "content-length"}
        }

        body = await request.body()
        query_string = request.url.query
        if query_string:
            target_url = f"{target_url}?{query_string}"

        async with httpx.AsyncClient(timeout=90.0) as client:
            upstream = await client.request(
                method=request.method,
                url=target_url,
                headers=filtered_headers,
                content=body,
            )

        response_headers = {
            key: value
            for key, value in upstream.headers.items()
            if key.lower() not in {"content-length", "transfer-encoding", "connection"}
        }
        return Response(
            content=upstream.content,
            status_code=upstream.status_code,
            headers=response_headers,
            media_type=upstream.headers.get("content-type"),
        )


proxy_service = ProxyService()
