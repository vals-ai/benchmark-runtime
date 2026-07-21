"""Shared runtime contracts for manifest-backed benchmark orchestrators."""

from benchmark_runtime.artifacts import RunArtifacts
from benchmark_runtime.backend import SandboxGenerationBackend, format_exception
from benchmark_runtime.bundle import AgentBundle, build_bundle_zip, load_bundle
from benchmark_runtime.client import auth_headers, build_client
from benchmark_runtime.contract import AgentContract, format_run_cmd
from benchmark_runtime.grading import evaluate_generation, score_evaluations
from benchmark_runtime.manifest import AgentSpec, BundleSpec, Manifest, TaskEntry
from benchmark_runtime.protocols import (
    EvaluationClientLike,
    ExecResultLike,
    GradingClientLike,
    SandboxLike,
    ScoringClientLike,
)
from benchmark_runtime.sandbox_env import preflight_model, resolve_sandbox_env
from benchmark_runtime.schemas import (
    EvalResult,
    EvalResultData,
    EvalStatus,
    EvaluateResponseRequest,
    FinalScoreResponse,
    GenerationResult,
    GenerationStatus,
    ScoreResult,
    Task,
)

__all__ = [
    "AgentBundle",
    "AgentContract",
    "AgentSpec",
    "BundleSpec",
    "EvalResult",
    "EvalResultData",
    "EvalStatus",
    "EvaluateResponseRequest",
    "EvaluationClientLike",
    "ExecResultLike",
    "FinalScoreResponse",
    "GenerationResult",
    "GenerationStatus",
    "GradingClientLike",
    "Manifest",
    "RunArtifacts",
    "SandboxGenerationBackend",
    "SandboxLike",
    "ScoreResult",
    "ScoringClientLike",
    "Task",
    "TaskEntry",
    "auth_headers",
    "build_bundle_zip",
    "build_client",
    "evaluate_generation",
    "format_exception",
    "format_run_cmd",
    "load_bundle",
    "preflight_model",
    "resolve_sandbox_env",
    "score_evaluations",
]
