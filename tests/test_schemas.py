from benchmark_runtime.schemas import (
    EvalResult,
    EvalResultData,
    EvalStatus,
    GenerationResult,
    GenerationStatus,
    ScoreResult,
    Task,
)


def test_task_allows_base_extra_and_typed_subclass_fields():
    t = Task(id="01", question="hello?", system_prompt="be helpful")  # pyright: ignore[reportCallIssue]
    assert t.timeout is None
    assert t.model_dump()["system_prompt"] == "be helpful"

    class ExtendedTask(Task):
        docker_image: str
        cwd: str

    t = ExtendedTask(id="01", question="fix bug", docker_image="acme/repo:tag", cwd="/repo")
    assert t.docker_image == "acme/repo:tag"
    assert t.cwd == "/repo"


def test_generation_result_round_trip():
    gen = GenerationResult(
        task_id="01",
        status=GenerationStatus.SUCCESS,
        data="42",
        question="what?",
        model="m",
        total_turns=3,
        generation_version="abc123",
    )
    raw = gen.model_dump(mode="json")
    assert raw["status"] == "success"
    assert raw["data"] == "42"
    assert "answer" not in raw
    rehydrated = GenerationResult.model_validate(raw)
    assert rehydrated == gen


def test_generation_result_accepts_legacy_answer_alias_without_writing_it():
    gen = GenerationResult.model_validate({
        "task_id": "01",
        "status": "success",
        "answer": "42",
    })
    assert gen.data == "42"
    assert gen.answer == "42"
    assert "answer" not in gen.model_dump(mode="json")


def test_eval_result_data_allows_extra_and_typed_subclass_fields():
    extra = EvalResultData(pass_percentage=0.83, eval_version="v1", llm_output="...")  # pyright: ignore[reportCallIssue]
    assert extra.model_dump()["llm_output"] == "..."

    class TypedEvalResultData(EvalResultData):
        llm_output: str
        check_results: list[dict]

    data = TypedEvalResultData(
        pass_percentage=0.83,
        eval_version="v1",
        llm_output="...",
        check_results=[{"check": 1}],
    )
    assert data.llm_output == "..."
    assert data.check_results == [{"check": 1}]


def test_backfills_weighted_from_sdk_key_and_preserves_extra():
    # Older evaluation payloads store the weighted score under pass_percentage_with_weight.
    d = EvalResultData.model_validate({"pass_percentage": 57.1, "pass_percentage_with_weight": 42.857})
    assert d.weighted_pass_percentage == 42.857
    dumped = d.model_dump(mode="json")
    assert dumped["pass_percentage_with_weight"] == 42.857


def test_native_weighted_name_is_unchanged():
    # Native payloads already use weighted_pass_percentage.
    d = EvalResultData.model_validate({"pass_percentage": 50.0, "weighted_pass_percentage": 55.0})
    assert d.weighted_pass_percentage == 55.0


def test_explicit_weighted_wins_over_extra():
    d = EvalResultData.model_validate({"weighted_pass_percentage": 55.0, "pass_percentage_with_weight": 42.0})
    assert d.weighted_pass_percentage == 55.0


def test_eval_and_score_result_round_trip():
    ev = EvalResult(
        task_id="01",
        status=EvalStatus.EVALUATED,
        result=EvalResultData(pass_percentage=0.5, eval_version="v1"),
    )
    raw = ev.model_dump(mode="json")
    rehydrated = EvalResult.model_validate(raw)
    assert rehydrated.status == EvalStatus.EVALUATED
    assert rehydrated.result is not None
    assert rehydrated.result.pass_percentage == 0.5

    ev = EvalResult(task_id="01", status=EvalStatus.DID_NOT_COMPLETE)
    assert ev.result is None
    assert ev.error is None

    sr = ScoreResult(
        tasks_evaluated=["01", "02"],
        final_score=0.62,
        metadata={"category_a": 0.5},
        complete=True,
    )
    raw = sr.model_dump(mode="json")
    rehydrated = ScoreResult.model_validate(raw)
    assert rehydrated == sr
