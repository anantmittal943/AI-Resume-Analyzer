from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.dependencies import get_current_user
from app.models import JobDescription, User
from app.schemas import JobCreate, JobOut

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobOut, status_code=status.HTTP_201_CREATED)
def create_job(
    payload: JobCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobOut:
    job = JobDescription(
        user_id=current_user.id,
        title=payload.title,
        company=payload.company,
        description=payload.description,
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return JobOut.model_validate(job)


@router.get("", response_model=list[JobOut])
def list_jobs(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[JobOut]:
    records = (
        db.query(JobDescription)
        .filter(JobDescription.user_id == current_user.id)
        .order_by(JobDescription.created_at.desc())
        .all()
    )
    return [JobOut.model_validate(item) for item in records]


@router.get("/{job_id}", response_model=JobOut)
def get_job(
    job_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobOut:
    job = (
        db.query(JobDescription)
        .filter(JobDescription.id == job_id, JobDescription.user_id == current_user.id)
        .first()
    )
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found")
    return JobOut.model_validate(job)
