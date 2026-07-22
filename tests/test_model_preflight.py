import pytest
from benchmark_runtime import preflight_model


def test_google_model_missing_key_raises():
    with pytest.raises(ValueError, match="GOOGLE_API_KEY"):
        preflight_model("google/example-model", {})


def test_google_model_with_key_passes():
    preflight_model("google/example-model", {"GOOGLE_API_KEY": "x"})


def test_byo_endpoint_skips_native_key_check():
    preflight_model("google/example-model", {"CUSTOM_ENDPOINT": "https://example.com"})


def test_unknown_provider_skipped():
    preflight_model("unknown-provider/example-model", {})
    preflight_model("example-model", {})


def test_preflight_model_rejects_bare_id_with_custom_endpoint():
    with pytest.raises(ValueError, match="<provider>/<model-name>"):
        preflight_model("example-model", {"CUSTOM_ENDPOINT": "https://ep.example/v1"})


def test_preflight_model_accepts_prefixed_id_with_custom_endpoint():
    preflight_model("openai/example-model", {"CUSTOM_ENDPOINT": "https://ep.example/v1"})
