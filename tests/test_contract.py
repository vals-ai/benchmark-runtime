from pathlib import Path
from typing import Any
import pytest
from benchmark_runtime.contract import AgentContract, format_run_cmd


def test_loads_fields_and_validates_problem_placeholder(tmp_path: Path):
    p = tmp_path / "contract.yaml"
    p.write_text(
        "name: example_agent\n"
        "install_cmd: bash setup.sh\n"
        "run_cmd: >-\n"
        "  example-agent run --model {model} --run-id test-run --skip-eval\n"
        "  --results-dir /app/results --problem {problem_statement_path} {task_id}\n"
        "final_output: /app/results/test-run\n"
    )
    c = AgentContract.from_yaml(p)
    assert c.name == "example_agent"
    assert c.install_cmd == "bash setup.sh"
    assert c.final_output == "/app/results/test-run"
    assert "{problem_statement_path}" in c.run_cmd


def test_run_cmd_must_contain_problem_placeholder(tmp_path: Path):
    p = tmp_path / "contract.yaml"
    p.write_text("name: x\nrun_cmd: my-agent --model {model}\n")
    with pytest.raises(ValueError, match="problem_statement_path"):
        AgentContract.from_yaml(p)


def test_format_run_cmd_fills_model_leaves_runtime_placeholders():
    out = format_run_cmd(
        "a --model {model} --problem {problem_statement_path} {task_id}",
        {"model": "provider/example-model"},
    )
    assert out == "a --model provider/example-model --problem {problem_statement_path} {task_id}"


def _contract(**kw: Any) -> AgentContract:
    base: dict[str, Any] = dict(
        name="example",
        run_cmd="run --model {model} {problem_statement_path}",
        final_output="/app/results",
    )
    base.update(kw)
    return AgentContract(**base)


def test_param_defaults_from_defaults():
    # Required runtime parameters are excluded; optional defaults are returned.
    c = _contract(
        defaults={
            "model": {"type": "str", "required": True},
            "auditor_model": {"type": "str", "required": False, "default": "provider/example-auditor"},
        }
    )
    assert c.param_defaults() == {"auditor_model": "provider/example-auditor"}


def test_param_defaults_from_kwargs():
    c = _contract(
        defaults={"model": {"type": "str", "required": True}},
        kwargs={
            "max_output_tokens": {"type": "int", "required": False, "default": 32000},
            "reasoning_effort": {"type": "str", "required": False, "default": ""},
        },
    )
    assert c.param_defaults() == {"max_output_tokens": "32000", "reasoning_effort": ""}


def test_param_defaults_model_override_protection():
    # An empty model default cannot override the runtime-selected model.
    c = _contract(defaults={"model": {"required": False, "default": ""}})
    assert c.param_defaults() == {}
    out = format_run_cmd(
        "run {model} {problem_statement_path}",
        {"model": "anthropic/x", **c.param_defaults()},
    )
    assert "anthropic/x" in out
    assert '""' not in out
    assert " " not in out.split("{problem_statement_path}")[0].replace("run anthropic/x ", "")


def test_format_run_cmd_resolves_defaults_and_keeps_runtime_placeholders():
    out = format_run_cmd(
        "run --model {model} --auditor-model {auditor_model} {problem_statement_path} {task_id}",
        {"model": "google/x", "auditor_model": "openai/y"},
    )
    assert out == "run --model google/x --auditor-model openai/y {problem_statement_path} {task_id}"


def test_format_run_cmd_raises_on_unresolved_placeholder():
    with pytest.raises(ValueError, match="auditor_model"):
        format_run_cmd("run --auditor-model {auditor_model} {problem_statement_path}", {"model": "m"})
