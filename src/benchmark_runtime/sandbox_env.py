"""Resolve and validate environment passed into task sandboxes."""

import os

from benchmark_runtime.contract import AgentContract


BYO_ENDPOINT_ENV_VARS = (
    "CUSTOM_ENDPOINT",
    "CUSTOM_API_KEY",
)


NATIVE_PROVIDER_KEY_ENV = {
    "openai": "OPENAI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
    "google": "GOOGLE_API_KEY",
    "mistral": "MISTRAL_API_KEY",
    "cohere": "COHERE_API_KEY",
    "xai": "XAI_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
}


def resolve_sandbox_env(
    contract: AgentContract,
    *,
    sandbox_env: list[str] | None = None,
) -> dict[str, str]:
    """Resolve only explicitly selected host environment variables."""
    env: dict[str, str] = {}
    missing: list[str] = []
    for var_name in contract.secrets:
        value = os.environ.get(var_name)
        if value:
            env[var_name] = value
        else:
            missing.append(var_name)
    if missing:
        raise ValueError("contract declares secret(s) not set in the host environment: " + ", ".join(sorted(missing)))

    runtime_missing: list[str] = []
    for var_name in dict.fromkeys(sandbox_env or []):
        value = os.environ.get(var_name)
        if value:
            env[var_name] = value
        else:
            runtime_missing.append(var_name)
    if runtime_missing:
        raise ValueError("sandbox env var(s) not set in the host environment: " + ", ".join(sorted(runtime_missing)))

    for var_name in BYO_ENDPOINT_ENV_VARS:
        value = os.environ.get(var_name)
        if value:
            env[var_name] = value

    endpoint = env.get("CUSTOM_ENDPOINT")
    if endpoint and not endpoint.startswith(("http://", "https://")):
        raise ValueError(
            f"CUSTOM_ENDPOINT is set but is not a URL ({endpoint!r}). Set it to an "
            "OpenAI-compatible base URL, or leave it empty to use the model's own API key."
        )
    return env


def preflight_model(model: str, secret_env: dict[str, str]) -> None:
    """Validate model routing before starting a task sandbox."""
    if "CUSTOM_ENDPOINT" in secret_env:
        provider, separator, name = model.partition("/")
        if not separator or not provider or not name:
            raise ValueError(
                f"--model {model!r} must be '<provider>/<model-name>' when CUSTOM_ENDPOINT is set. "
                "The provider prefix selects the client protocol used to call your endpoint "
                "(e.g. openai/<your-model-id> for an OpenAI-compatible endpoint); "
                "<model-name> is sent to your endpoint as the model field."
            )
        return

    provider = model.split("/", 1)[0] if "/" in model else ""
    key_env = NATIVE_PROVIDER_KEY_ENV.get(provider)
    if key_env and key_env not in secret_env:
        raise ValueError(
            f"model '{model}' needs {key_env} inside the task sandbox, but it is not "
            f"forwarded. Add {key_env} to the manifest's agent.required_env, pass "
            f"--sandbox-env {key_env}, or set CUSTOM_ENDPOINT/CUSTOM_API_KEY to route "
            "generation through your own endpoint."
        )


__all__ = ["BYO_ENDPOINT_ENV_VARS", "NATIVE_PROVIDER_KEY_ENV", "preflight_model", "resolve_sandbox_env"]
