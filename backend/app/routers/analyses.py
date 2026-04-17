import json

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.dependencies import get_current_user
from app.models import Analysis, JobDescription, Resume, User
from app.schemas import AnalysisCreate, AnalysisHistoryPage, AnalysisOut, KeywordMatch
from app.services.analysis import run_analysis

router = APIRouter(prefix="/analyses", tags=["analyses"])


def _analysis_to_schema(record: Analysis) -> AnalysisOut:
    strengths = json.loads(record.strengths_json)
    gaps = json.loads(record.gaps_json)
    keyword_breakdown = json.loads(record.keyword_breakdown_json)

    return AnalysisOut(
        id=record.id,
        resume_id=record.resume_id,
        job_id=record.job_id,
        suitability_score=record.suitability_score,
        summary=record.summary,
        strengths=[str(item) for item in strengths],
        gaps=[str(item) for item in gaps],
        keyword_breakdown=[KeywordMatch(**item) for item in keyword_breakdown],
        provider_used=record.provider_used,
        created_at=record.created_at,
    )


@router.post("", response_model=AnalysisOut, status_code=status.HTTP_201_CREATED)
def create_analysis(
    payload: AnalysisCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AnalysisOut:
    resume = (
        db.query(Resume)
        .filter(Resume.id == payload.resume_id, Resume.user_id == current_user.id)
        .first()
    )
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    job = (
        db.query(JobDescription)
        .filter(JobDescription.id == payload.job_id, JobDescription.user_id == current_user.id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")

    settings = get_settings()
    result, provider_used = run_analysis(
        resume_text=resume.extracted_text,
        job_text=job.description,
        settings=settings,
    )

    analysis = Analysis(
        user_id=current_user.id,
        resume_id=resume.id,
        job_id=job.id,
        suitability_score=result["suitability_score"],
        summary=result["summary"],
        strengths_json=json.dumps(result["strengths"]),
        gaps_json=json.dumps(result["gaps"]),
        keyword_breakdown_json=json.dumps(result["keyword_breakdown"]),
        provider_used=provider_used,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    return _analysis_to_schema(analysis)


@router.get("/history", response_model=AnalysisHistoryPage)
def list_analysis_history(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> AnalysisHistoryPage:
    base_query = db.query(Analysis).filter(Analysis.user_id == current_user.id)
    total = base_query.count()
    records = base_query.order_by(Analysis.created_at.desc()).offset(offset).limit(limit).all()

    return AnalysisHistoryPage(
        total=total,
        limit=limit,
        offset=offset,
        items=[_analysis_to_schema(record) for record in records],
    )
