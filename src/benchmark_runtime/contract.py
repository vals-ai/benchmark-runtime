import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, field_validator

# Filled per-task in-sandbox by the generation backend, so format_run_cmd leaves them.
RUNTIME_PLACEHOLDERS = ("problem_statement_path", "task_id")


class AgentContract(BaseModel):
    name: str
    run_cmd: str
    install_cmd: str | None = None
    final_output: str | None = None
    secrets: dict[str, str] = {}
    defaults: dict[str, Any] = {}
    kwargs: dict[str, Any] = {}

    @field_validator("run_cmd")
    @classmethod
    def _require_problem_placeholder(cls, v: str) -> str:
        if "{problem_statement_path}" not in v:
            raise ValueError("run_cmd must contain {problem_statement_path}")
        return v

    @classmethod
    def from_yaml(cls, path: Path) -> "AgentContract":
        data = yaml.safe_load(Path(path).read_text())
        if data.get("final_output") is not None:
            data["final_output"] = str(data["final_output"])
        return cls.model_validate(data)

    def param_defaults(self) -> dict[str, str]:
        """Fill values for run_cmd placeholders: every declared param (in `defaults`
        or `kwargs`) that carries a `default`, EXCEPT `model` — which is always
        supplied at runtime via --model, never sourced from the contract."""
        values: dict[str, str] = {}
        for block in (self.defaults, self.kwargs):
            for name, spec in block.items():
                if name == "model":
                    continue
                if isinstance(spec, Mapping) and "default" in spec:
                    values[name] = str(spec["default"])
        return values


def format_run_cmd(run_cmd: str, kwargs: dict[str, Any]) -> str:
    """Fill {model} and other declared kwargs. Leaves {problem_statement_path}
    and {task_id} for in-sandbox substitution; any OTHER surviving placeholder is
    a configuration error and raises rather than leaking a literal into the shell."""
    out = run_cmd
    for key, value in kwargs.items():
        out = out.replace("{" + key + "}", str(value))
    unresolved = sorted(
        {name for name in re.findall(r"\{(\w+)\}", out) if name not in RUNTIME_PLACEHOLDERS}
    )
    if unresolved:
        raise ValueError(
            "run_cmd has unresolved placeholder(s) "
            + ", ".join("{" + n + "}" for n in unresolved)
            + "; declare them in the contract's `defaults` or pass them explicitly"
        )
    return out
