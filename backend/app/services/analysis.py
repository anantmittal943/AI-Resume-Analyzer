import re
from typing import Any

from app.config import Settings
from app.services.providers import analyze_with_fallback

STOP_WORDS = {
    "about",
    "after",
    "again",
    "also",
    "among",
    "and",
    "are",
    "because",
    "been",
    "but",
    "for",
    "from",
    "have",
    "into",
    "like",
    "must",
    "required",
    "that",
    "their",
    "them",
    "this",
    "with",
    "your",
}


def _tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9+#.]{2,}", text.lower())
    return [token for token in tokens if token not in STOP_WORDS]


def _extract_keywords(job_text: str, limit: int = 24) -> list[str]:
    frequencies: dict[str, int] = {}
    for token in _tokenize(job_text):
        frequencies[token] = frequencies.get(token, 0) + 1
    ranked = sorted(frequencies.items(), key=lambda item: (-item[1], item[0]))
    return [token for token, _ in ranked[:limit]]


def _keyword_breakdown(keywords: list[str], resume_text: str) -> list[dict[str, Any]]:
    haystack = resume_text.lower()
    return [{"keyword": keyword, "matched": keyword in haystack} for keyword in keywords]


def _heuristic_analysis(resume_text: str, job_text: str) -> dict[str, Any]:
    keywords = _extract_keywords(job_text)
    breakdown = _keyword_breakdown(keywords, resume_text)
    matched = [item["keyword"] for item in breakdown if item["matched"]]
    missing = [item["keyword"] for item in breakdown if not item["matched"]]
    score = int(round((len(matched) / max(len(keywords), 1)) * 100))

    return {
        "suitability_score": max(0, min(score, 100)),
        "summary": (
            f"Heuristic evaluation completed. Matched {len(matched)} of {len(keywords)} key terms."
        ),
        "strengths": matched[:8],
        "gaps": missing[:8],
        "keyword_breakdown": breakdown,
    }


def _coerce_output(data: dict[str, Any]) -> dict[str, Any]:
    breakdown = data.get("keyword_breakdown", [])
    normalized_breakdown = []
    for item in breakdown:
        if isinstance(item, dict) and "keyword" in item:
            normalized_breakdown.append(
                {"keyword": str(item["keyword"]), "matched": bool(item.get("matched", False))}
            )

    score = int(data.get("suitability_score", 0))
    return {
        "suitability_score": max(0, min(score, 100)),
        "summary": str(data.get("summary", ""))[:4000],
        "strengths": [str(item) for item in data.get("strengths", [])][:8],
        "gaps": [str(item) for item in data.get("gaps", [])][:8],
        "keyword_breakdown": normalized_breakdown[:30],
    }


def run_analysis(resume_text: str, job_text: str, settings: Settings) -> tuple[dict[str, Any], str]:
    provider_data, provider_used = analyze_with_fallback(resume_text, job_text, settings)
    if provider_data:
        coerced = _coerce_output(provider_data)
        if coerced["keyword_breakdown"]:
            return coerced, provider_used

    fallback = _heuristic_analysis(resume_text=resume_text, job_text=job_text)
    return fallback, "heuristic"
