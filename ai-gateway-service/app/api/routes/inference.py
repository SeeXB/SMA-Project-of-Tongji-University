from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status

from app.models.inference import (
    InferAsyncRequest,
    InferAsyncResponse,
    InferResultResponse,
    InferSyncRequest,
    InferSyncResponse,
    TokenStatisticResponse,
)
from app.services.inference_service import InferenceService, get_inference_service

router = APIRouter(prefix="/ai", tags=["AI Gateway"])


@router.post(
    "/infer-sync",
    response_model=InferSyncResponse,
    status_code=status.HTTP_200_OK,
    summary="Run synchronous AI inference",
)
async def infer_sync(
    request: InferSyncRequest,
    inference_service: InferenceService = Depends(get_inference_service),
) -> InferSyncResponse:
    try:
        return await inference_service.infer_sync(request)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post(
    "/infer-async",
    response_model=InferAsyncResponse,
    status_code=status.HTTP_202_ACCEPTED,
    summary="Submit asynchronous AI inference",
)
async def infer_async(
    request: InferAsyncRequest,
    inference_service: InferenceService = Depends(get_inference_service),
) -> InferAsyncResponse:
    try:
        return await inference_service.infer_async(request)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get(
    "/result/{task_id}",
    response_model=InferResultResponse,
    status_code=status.HTTP_200_OK,
    summary="Query asynchronous AI result",
)
async def get_result(
    task_id: str,
    inference_service: InferenceService = Depends(get_inference_service),
) -> InferResultResponse:
    return inference_service.get_result(task_id)


@router.get(
    "/token-statistic",
    response_model=TokenStatisticResponse,
    status_code=status.HTTP_200_OK,
    summary="Get token usage statistics",
)
async def token_statistic(
    user_id: Optional[str] = None,
    inference_service: InferenceService = Depends(get_inference_service),
) -> TokenStatisticResponse:
    return inference_service.get_token_statistics(user_id)
