from app.config import Settings
from app.services.analysis import run_analysis


def test_heuristic_analysis_returns_expected_shape() -> None:
    settings = Settings(gemini_api_key=None, groq_api_key=None)
    resume_text = "Python FastAPI SQL Docker CI/CD testing and APIs"
    job_text = "Looking for Python developer with FastAPI and Docker skills"

    result, provider = run_analysis(resume_text=resume_text, job_text=job_text, settings=settings)

    assert provider == "heuristic"
    assert 0 <= result["suitability_score"] <= 100
    assert isinstance(result["strengths"], list)
    assert isinstance(result["gaps"], list)
    assert isinstance(result["keyword_breakdown"], list)
