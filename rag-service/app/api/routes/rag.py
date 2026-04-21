from fastapi import APIRouter, Depends, HTTPException, status

from app.models.rag import RagRetrievalRequest, RagRetrievalResponse, RagStoreRequest, RagStoreResponse
from app.services.rag_service import RagService, get_rag_service

router = APIRouter(prefix="/rag", tags=["RAG"])


@router.post("/store", response_model=RagStoreResponse, status_code=202)
async def store(
    request: RagStoreRequest,
    rag_service: RagService = Depends(get_rag_service),
) -> RagStoreResponse:
    try:
        return await rag_service.store(request)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc


@router.post("/retrieval", response_model=RagRetrievalResponse)
async def retrieval(
    request: RagRetrievalRequest,
    rag_service: RagService = Depends(get_rag_service),
) -> RagRetrievalResponse:
    try:
        return await rag_service.retrieval(request)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
