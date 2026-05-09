from typing import Literal, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class InferSyncRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    capability: Literal[
        "slide-summary",
        "quiz-generation",
        "qa",
        "grading-suggestion",
        "moderation",
        "ai-detection",
    ]
    prompt: str = Field(..., min_length=1, max_length=20000)
    trace_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        validation_alias=AliasChoices("trace_id", "traceId"),
        serialization_alias="traceId",
    )
    user_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        validation_alias=AliasChoices("user_id", "userId"),
        serialization_alias="userId",
    )
    metadata: dict[str, str] = Field(default_factory=dict)


class InferSyncResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    capability: str
    trace_id: str = Field(serialization_alias="traceId")
    output_text: str = Field(serialization_alias="outputText")
    provider: str
    model: str


class InferAsyncRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    capability: str
    prompt: str = Field(..., min_length=1, max_length=20000)
    user_id: str = Field(
        ...,
        min_length=1,
        max_length=100,
        validation_alias=AliasChoices("user_id", "userId"),
        serialization_alias="userId",
    )
    callback_url: Optional[str] = Field(
        default=None,
        validation_alias=AliasChoices("callback_url", "callbackUrl"),
        serialization_alias="callbackUrl",
    )
    metadata: dict[str, str] = Field(default_factory=dict)


class InferAsyncResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    task_id: str = Field(serialization_alias="taskId")
    status: str
    accepted_at: str = Field(serialization_alias="acceptedAt")


class InferResultResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    task_id: str = Field(serialization_alias="taskId")
    status: str
    output_text: Optional[str] = Field(default=None, serialization_alias="outputText")
    error_message: Optional[str] = Field(default=None, serialization_alias="errorMessage")


class TokenStatisticResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: Optional[str] = Field(default=None, serialization_alias="userId")
    total_prompt_tokens: int = Field(serialization_alias="totalPromptTokens")
    total_completion_tokens: int = Field(serialization_alias="totalCompletionTokens")
    total_cost_usd: float = Field(serialization_alias="totalCostUsd")
