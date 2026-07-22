"""Benchmark manifest schema shared by lab-hosted benchmark orchestrators.

This module owns only the manifest shape that orchestrators consume. Generating a
manifest (querying a deployed service for tasks/images/versions) is an internal
concern and lives in the manifest generator, not in this lab-facing package.
"""

from pydantic import BaseModel, model_validator

from benchmark_service.sandbox import Resources


class BundleSpec(BaseModel):
    """Pin for the agent bundle zip delivered alongside the manifest.

    ``file`` is relative to the manifest's own location. The orchestrator
    extracts the zip to /bundle/<its top-level dir> in every sandbox and runs
    install_cmd there; no bundle means the task images prebake the agent.
    """

    file: str
    sha256: str


class AgentSpec(BaseModel):
    bundle: BundleSpec | None = None
    install_cmd: str | None
    run_cmd: str
    final_output: str | None
    # Lab-facing env var names supplied by packaging metadata, not contract.yaml.
    required_env: list[str] = []

    @model_validator(mode="after")
    def _install_cmd_requires_bundle(self) -> "AgentSpec":
        if self.install_cmd is not None and self.bundle is None:
            raise ValueError(
                "agent.install_cmd requires agent.bundle (prebaked task images need no install step)"
            )
        return self


class EvalSpec(BaseModel):
    evaluate_endpoint: str
    score_endpoint: str
    payload_schema: str


class TaskEntry(BaseModel):
    id: str
    question: str
    timeout: float | None
    image: str
    resources: Resources
    cwd: str
    # In-sandbox path where the agent expects the problem statement.
    problem_path: str


class ServiceSpec(BaseModel):
    url: str


class DatasetSpec(BaseModel):
    name: str


class VersionsSpec(BaseModel):
    """Pinned versions a score traces back to; a field is null until its source is wired.

    framework/service/dataset come from the service's /version — dataset is the declared
    label (source of truth for repo-local services). dataset_fingerprint is a content hash
    of the task set: it catches silent task-set edits and is the only dataset signal for
    services that declare no label. New version dimensions are added here as sources are exposed.
    """

    framework: str | None = None
    service: str | None = None
    dataset: str | None = None
    dataset_fingerprint: str | None = None


class Manifest(BaseModel):
    benchmark: str
    service: ServiceSpec
    dataset: DatasetSpec
    agent: AgentSpec
    eval: EvalSpec
    versions: VersionsSpec
    tasks: list[TaskEntry]


__all__ = [
    "AgentSpec",
    "BundleSpec",
    "DatasetSpec",
    "EvalSpec",
    "Manifest",
    "ServiceSpec",
    "TaskEntry",
    "VersionsSpec",
]
