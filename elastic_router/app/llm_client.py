"""
GreenWeave — Elastic Router
LLM Client: Forwards the prompt to the chosen model API.

Supports:
  • OpenAI-compatible APIs  (openai, groq — same SDK)
  • Anthropic API           (anthropic)

The frontend NEVER knows which model answered — full abstraction.
"""

import time
from dataclasses import dataclass

from app.config import ModelConfig, API_KEY_MAP, MAX_TOKENS
from app.logger import get_logger

logger = get_logger("llm_client")


@dataclass
class LLMResponse:
    text: str
    model_id: str
    latency_ms: float
    prompt_tokens: int
    completion_tokens: int


def call_model(
    model: ModelConfig,
    messages: list[dict],
    system_prompt: str | None = None,
) -> LLMResponse:
    """
    Route the prompt to the correct LLM provider.

    Args:
        model:         ModelConfig chosen by router_logic
        messages:      list of {"role": "user"/"assistant", "content": "..."}
        system_prompt: optional system instruction

    Returns:
        LLMResponse with text, latency, and token counts
    """
    api_key = API_KEY_MAP.get(model.api_key_env, "")

    if not api_key:
        raise ValueError(
            f"API key for {model.api_key_env} not set in .env"
        )

    provider = model.provider.lower()

    if provider in ("openai", "groq"):
        return _call_openai_compatible(model, messages, system_prompt, api_key)
    elif provider == "anthropic":
        return _call_anthropic(model, messages, system_prompt, api_key)
    else:
        raise ValueError(f"Unknown provider: {model.provider}")


# ─────────────────────────────────────────────
#  OpenAI-compatible  (OpenAI + Groq share the same SDK)
# ─────────────────────────────────────────────

def _call_openai_compatible(
    model: ModelConfig,
    messages: list[dict],
    system_prompt: str | None,
    api_key: str,
) -> LLMResponse:
    from openai import OpenAI
    import httpx  # IMPORTED HTTPX TO FIX THE PROXY BUG

    base_url = (
        "https://api.groq.com/openai/v1"
        if model.provider.lower() == "groq"
        else None            # OpenAI default
    )

    # FIX: We build the custom HTTP client ourselves to stop the OpenAI library 
    # from crashing when it tries to use the deleted 'proxies' keyword!
    custom_http_client = httpx.Client()

    client = OpenAI(
        api_key=api_key, 
        base_url=base_url,
        http_client=custom_http_client  # Passing our bug-free client
    )

    # Prepend system message if provided
    full_messages = []
    if system_prompt:
        full_messages.append({"role": "system", "content": system_prompt})
    full_messages.extend(messages)

    logger.info("Calling %s | model=%s", model.provider, model.model_id)
    t0 = time.perf_counter()

    response = client.chat.completions.create(
        model=model.model_id,
        messages=full_messages,
        max_tokens=MAX_TOKENS,
        temperature=0.7,
    )

    latency_ms = (time.perf_counter() - t0) * 1000

    return LLMResponse(
        text=response.choices[0].message.content,
        model_id=model.model_id,
        latency_ms=round(latency_ms, 1),
        prompt_tokens=response.usage.prompt_tokens,
        completion_tokens=response.usage.completion_tokens,
    )


# ─────────────────────────────────────────────
#  Anthropic
# ─────────────────────────────────────────────

def _call_anthropic(
    model: ModelConfig,
    messages: list[dict],
    system_prompt: str | None,
    api_key: str,
) -> LLMResponse:
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)

    logger.info("Calling Anthropic | model=%s", model.model_id)
    t0 = time.perf_counter()

    kwargs = dict(
        model=model.model_id,
        messages=messages,
        max_tokens=MAX_TOKENS,
    )
    if system_prompt:
        kwargs["system"] = system_prompt

    response = client.messages.create(**kwargs)

    latency_ms = (time.perf_counter() - t0) * 1000

    return LLMResponse(
        text=response.content[0].text,
        model_id=model.model_id,
        latency_ms=round(latency_ms, 1),
        prompt_tokens=response.usage.input_tokens,
        completion_tokens=response.usage.output_tokens,
    )