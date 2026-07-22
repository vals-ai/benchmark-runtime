"""Schema-level tests for the manifest models (generation lives in the registry)."""

import pytest
from pydantic import ValidationError

from benchmark_runtime.manifest import AgentSpec


def test_agent_spec_rejects_install_cmd_without_bundle() -> None:
    """An install command is valid only when a manifest pins a bundle."""
    with pytest.raises(ValidationError, match="install_cmd requires agent.bundle"):
        AgentSpec(
            bundle=None,
            install_cmd="bash setup.sh",
            run_cmd="run --problem {problem_statement_path}",
            final_output="/app/results",
        )
