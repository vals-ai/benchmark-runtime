"""Runner-side schemas."""

from enum import StrEnum
from typing import Any

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, model_validator

from benchmark_service.schemas import (
    EvaluateResponseRequest,
    FinalScoreResponse,
)


class Task(BaseModel):
    model_config = ConfigDict(extra="allow")
    id: str
    question: str
    timeout: float | None = None


class GenerationStatus(StrEnum):
    SUCCESS = "success"
    MAX_TIME = "max_time"
    MAX_TURNS = "max_turns"
    ERROR = "error"


class GenerationResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    task_id: str
    status: GenerationStatus
    data: str = Field(validation_alias=AliasChoices("data", "answer"))
    question: str | None = None
    model: str | None = None
    total_turns: int | None = None
    error: str | None = None
    log_dir: str | None = None
    generation_version: str | None = None

    @property
    def answer(self) -> str:
        return self.data


class EvalStatus(StrEnum):
    EVALUATED = "evaluated"
    DID_NOT_COMPLETE = "did_not_complete"
    GENERATION_ERROR = "generation_error"
    ERROR = "error"


class EvalResultData(BaseModel):
    model_config = ConfigDict(extra="allow")
    pass_percentage: float | None = None
    weighted_pass_percentage: float | None = None
    eval_version: str | None = None

    @model_validator(mode="after")
    def _backfill_weighted_from_sdk_key(self) -> "EvalResultData":
        # Preserve the SDK-named extra because final scoring may read it again.
        if self.weighted_pass_percentage is None and self.__pydantic_extra__:
            sdk_value = self.__pydantic_extra__.get("pass_percentage_with_weight")
            if sdk_value is not None:
                self.weighted_pass_percentage = float(sdk_value)
        return self


class EvalResult(BaseModel):
    task_id: str
    status: EvalStatus
    result: EvalResultData | None = None
    error: str | None = None


class ScoreResult(BaseModel):
    tasks_evaluated: list[str]
    final_score: float
    metadata: dict[str, Any]
    complete: bool = False

    @property
    def mean_weighted_pass_percentage(self) -> float | None:
        """Headline metric (0-100), when the service reports it in metadata."""
        value = self.metadata.get("mean_weighted_pass_percentage")
        return float(value) if value is not None else None


__all__ = [
    "EvalResult",
    "EvalResultData",
    "EvalStatus",
    "EvaluateResponseRequest",
    "FinalScoreResponse",
    "GenerationResult",
    "GenerationStatus",
    "ScoreResult",
    "Task",
]
