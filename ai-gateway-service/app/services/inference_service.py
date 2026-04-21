from functools import lru_cache
from datetime import datetime, timezone
from typing import List, Optional, Union
from uuid import uuid4

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from app.core.config import Settings, get_settings
from app.models.inference import (
    InferAsyncRequest,
    InferAsyncResponse,
    InferResultResponse,
    InferSyncRequest,
    InferSyncResponse,
    TokenStatisticResponse,
)

try:
    from langchain_openai import ChatOpenAI
except ImportError:  # pragma: no cover - dependency is declared in requirements.txt
    ChatOpenAI = None


class InferenceService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._tasks: dict[str, dict] = {}
        self._token_usage: list[dict] = []

    async def infer_sync(self, request: InferSyncRequest) -> InferSyncResponse:
        prompt = self._build_prompt(request)
        output_text = await self._generate_text(prompt)
        self._record_usage(request.user_id, request.prompt, output_text)
        return InferSyncResponse(
            capability=request.capability,
            trace_id=request.trace_id,
            output_text=output_text,
            provider=self.settings.llm_provider,
            model=self.settings.openai_model if self.settings.llm_provider.lower() == "openai" else "mock-llm",
        )

    async def infer_async(self, request: InferAsyncRequest) -> InferAsyncResponse:
        task_id = str(uuid4())
        accepted_at = self._now()
        self._tasks[task_id] = {
            "status": "running",
            "output_text": None,
            "error_message": None,
            "accepted_at": accepted_at,
        }

        sync_response = await self.infer_sync(
            InferSyncRequest(
                capability=request.capability,
                prompt=request.prompt,
                traceId=task_id,
                userId=request.user_id,
                metadata=request.metadata,
            )
        )
        self._tasks[task_id] = {
            "status": "succeeded",
            "output_text": sync_response.output_text,
            "error_message": None,
            "accepted_at": accepted_at,
        }
        return InferAsyncResponse(task_id=task_id, status="succeeded", accepted_at=accepted_at)

    def get_result(self, task_id: str) -> InferResultResponse:
        task = self._tasks.get(task_id)
        if not task:
            return InferResultResponse(task_id=task_id, status="not_found", error_message="Task not found")
        return InferResultResponse(
            task_id=task_id,
            status=task["status"],
            output_text=task["output_text"],
            error_message=task["error_message"],
        )

    def get_token_statistics(self, user_id: Optional[str] = None) -> TokenStatisticResponse:
        records = [item for item in self._token_usage if user_id is None or item["user_id"] == user_id]
        total_prompt_tokens = sum(item["prompt_tokens"] for item in records)
        total_completion_tokens = sum(item["completion_tokens"] for item in records)
        total_cost_usd = round(sum(item["cost_usd"] for item in records), 6)
        return TokenStatisticResponse(
            user_id=user_id,
            total_prompt_tokens=total_prompt_tokens,
            total_completion_tokens=total_completion_tokens,
            total_cost_usd=total_cost_usd,
        )

    def _build_prompt(self, request: InferSyncRequest) -> List[Union[SystemMessage, HumanMessage]]:
        if request.capability == "slide-summary":
            system_instruction = (
                "You are an academic assistant. Summarize the provided course slides into a concise, "
                "student-friendly overview with key takeaways."
            )
        else:
            system_instruction = "You are a helpful academic AI assistant."

        template = ChatPromptTemplate.from_messages(
            [
                ("system", system_instruction),
                ("human", "{prompt}"),
            ]
        )
        return template.format_messages(prompt=request.prompt)

    async def _generate_text(self, messages: List[Union[SystemMessage, HumanMessage]]) -> str:
        if self.settings.llm_provider.lower() == "openai":
            if ChatOpenAI is None:
                raise ValueError("langchain-openai dependency is missing.")
            if not self.settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY must be configured when llm_provider=openai.")

            model = ChatOpenAI(
                api_key=self.settings.openai_api_key,
                base_url=self.settings.openai_base_url,
                model=self.settings.openai_model,
                timeout=self.settings.request_timeout_seconds,
                temperature=0.2,
            )
            response = await model.ainvoke(messages)
            return str(response.content).strip()

        slide_text = next((message.content for message in messages if isinstance(message, HumanMessage)), "")
        compact = " ".join(str(slide_text).split())
        return (
            "Mock summary: "
            + (compact[:400] + "..." if len(compact) > 400 else compact)
        )

    def _record_usage(self, user_id: str, prompt: str, output_text: str) -> None:
        prompt_tokens = max(1, len(prompt.split()))
        completion_tokens = max(1, len(output_text.split()))
        self._token_usage.append(
            {
                "user_id": user_id,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "cost_usd": (prompt_tokens + completion_tokens) * 0.000001,
            }
        )

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()


@lru_cache(maxsize=1)
def get_inference_service() -> InferenceService:
    return InferenceService(get_settings())
