"""OpenRouter-backed LLM client (OpenAI-compatible) + structured JSON helper.

Free models don't reliably honour JSON mode, so we prompt for raw JSON, extract
it defensively, validate against a Pydantic schema, and retry once on failure.
"""

from __future__ import annotations

from typing import Any, cast

from openai import AsyncOpenAI
from pydantic import BaseModel, ValidationError

from app.config import get_settings


def get_client() -> AsyncOpenAI:
    """Build an OpenAI-compatible client pointed at OpenRouter."""
    settings = get_settings()
    return AsyncOpenAI(
        api_key=settings.openrouter_api_key,
        base_url=settings.openrouter_base_url,
    )


def extract_json(text: str) -> str:
    """Pull the JSON object out of a model response (handles code fences/prose)."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        parts = cleaned.split("```")
        if len(parts) >= 2:
            cleaned = parts[1]
        cleaned = cleaned.removeprefix("json").strip()
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        return cleaned[start : end + 1]
    return cleaned


async def _chat(
    client: AsyncOpenAI,
    model: str,
    messages: list[dict[str, str]],
    max_tokens: int,
) -> str:
    response = await client.chat.completions.create(
        model=model,
        messages=cast(Any, messages),
        max_tokens=max_tokens,
        temperature=0.3,
    )
    return response.choices[0].message.content or ""


async def complete_json[T: BaseModel](
    *,
    system: str,
    user: str,
    schema: type[T],
    model: str,
    max_tokens: int = 4000,
) -> T:
    """Call the model and return a validated instance of ``schema``."""
    client = get_client()
    instruction = "\n\nReturn ONLY valid JSON matching the requested schema. No markdown, no prose."
    messages: list[dict[str, str]] = [
        {"role": "system", "content": system + instruction},
        {"role": "user", "content": user},
    ]

    raw = await _chat(client, model, messages, max_tokens)
    try:
        return schema.model_validate_json(extract_json(raw))
    except (ValidationError, ValueError) as err:
        messages.append({"role": "assistant", "content": raw})
        messages.append(
            {
                "role": "user",
                "content": (
                    f"That response was invalid: {err}. "
                    "Fix it and return ONLY valid JSON matching the schema. No prose."
                ),
            }
        )
        raw = await _chat(client, model, messages, max_tokens)
        return schema.model_validate_json(extract_json(raw))
