import json
import logging
from collections.abc import Callable
from typing import Any, cast

import requests

from app.config import Settings

logger = logging.getLogger(__name__)

ProviderCallable = Callable[[str, Settings], dict[str, Any]]


def _build_prompt(resume_text: str, job_text: str) -> str:
    return (
        "You are an expert hiring analyst. "
        "Compare a resume against a job description and output JSON only. "
        "Schema: {"
        '"suitability_score": int 0..100,'
        '"summary": string,'
        '"strengths": [string],'
        '"gaps": [string],'
        '"keyword_breakdown": [{"keyword": string, "matched": bool}]'
        "}. Keep arrays concise (max 8 items each)."
        f"\n\nRESUME:\n{resume_text[:12000]}\n\nJOB DESCRIPTION:\n{job_text[:12000]}"
    )


def _extract_json_blob(text: str) -> dict[str, Any]:
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or start >= end:
        raise ValueError("No JSON object found in model response")
    return cast(dict[str, Any], json.loads(text[start : end + 1]))


def _call_gemini(prompt: str, settings: Settings) -> dict[str, Any]:
    if not settings.gemini_api_key:
        raise RuntimeError("Gemini API key not configured")

    endpoint = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{settings.gemini_model}:generateContent?key={settings.gemini_api_key}"
    )
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.2},
    }
    response = requests.post(endpoint, json=payload, timeout=settings.provider_timeout_seconds)
    response.raise_for_status()
    data = response.json()
    parts = data["candidates"][0]["content"]["parts"]
    text = "".join(part.get("text", "") for part in parts)
    return _extract_json_blob(text)


def _call_groq(prompt: str, settings: Settings) -> dict[str, Any]:
    if not settings.groq_api_key:
        raise RuntimeError("Groq API key not configured")

    endpoint = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {settings.groq_api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": settings.groq_model,
        "temperature": 0.2,
        "messages": [
            {
                "role": "system",
                "content": "Return strict JSON with no markdown and no explanations.",
            },
            {"role": "user", "content": prompt},
        ],
    }
    response = requests.post(
        endpoint,
        headers=headers,
        json=payload,
        timeout=settings.provider_timeout_seconds,
    )
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"]
    return _extract_json_blob(content)


def analyze_with_fallback(
    resume_text: str,
    job_text: str,
    settings: Settings,
) -> tuple[dict[str, Any] | None, str]:
    prompt = _build_prompt(resume_text=resume_text, job_text=job_text)

    providers: list[tuple[str, ProviderCallable]] = []
    if settings.gemini_api_key:
        providers.append(("gemini", _call_gemini))
    if settings.groq_api_key:
        providers.append(("groq", _call_groq))

    for provider_name, provider_fn in providers:
        try:
            return provider_fn(prompt, settings), provider_name
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Provider call failed",
                extra={"provider": provider_name, "action": str(exc)},
            )

    return None, "heuristic"
