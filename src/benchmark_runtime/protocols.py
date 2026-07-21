"""Structural interfaces between benchmark runtimes and their collaborators.

Protocols rather than the cbs ABCs so tests and alternate implementations only
need the methods the loop actually calls.
"""

from collections.abc import Callable
from typing import Any, Protocol

from benchmark_service.client import VerifyTaskIdsResponse
from benchmark_service.sandbox import SandboxCreateRequest, SandboxProviderConfig


class ExecResultLike(Protocol):
    exit_code: int
    output: str


class SandboxLike(Protocol):
    async def exec(self, command: str, *, cwd: str | None = None, timeout: float | None = None) -> ExecResultLike: ...
    async def upload_file(self, remote_path: str, content: bytes) -> None: ...
    async def download_file(self, remote_path: str) -> bytes: ...


class SandboxProviderLike(Protocol):
    async def create_sandbox(self, request: SandboxCreateRequest) -> Any: ...
    async def delete_sandbox(self, instance_id: str) -> None: ...


class GradingClientLike(Protocol):
    async def evaluate_response(self, task_id: str, response: str, dataset: str | None = None) -> Any: ...
    async def final_score(self, evaluation_results: dict[str, Any], dataset: str | None = None) -> Any: ...


class BenchmarkServiceClientLike(GradingClientLike, Protocol):
    def get_sandbox_provider(self, provider: SandboxProviderConfig) -> SandboxProviderLike: ...
    async def verify_task_ids(
        self, task_ids: list[str] | None, slice_str: str | None, dataset: str | None = None
    ) -> VerifyTaskIdsResponse: ...
    async def retrieve_task(self, task_id: str, skip_validation: bool = False, dataset: str | None = None) -> Any: ...
    async def setup_task(
        self,
        task_id: str,
        instance_id: str,
        sandbox_provider: SandboxProviderConfig | None = None,
        on_message: Callable[[str], None] | None = None,
        dataset: str | None = None,
    ) -> Any: ...


__all__ = [
    "BenchmarkServiceClientLike",
    "ExecResultLike",
    "GradingClientLike",
    "SandboxLike",
    "SandboxProviderLike",
]
