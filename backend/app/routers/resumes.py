from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.dependencies import get_current_user
from app.models import Resume, User
from app.schemas import ResumeOut
from app.services.file_parser import parse_and_store_resume

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("", response_model=ResumeOut, status_code=status.HTTP_201_CREATED)
def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResumeOut:
    settings = get_settings()
    file_path, extracted_text, mime_type, file_size = parse_and_store_resume(file, settings)

    resume = Resume(
        user_id=current_user.id,
        filename=file.filename or "resume",
        file_path=file_path,
        mime_type=mime_type,
        file_size=file_size,
        extracted_text=extracted_text,
    )
    db.add(resume)
    db.commit()
    db.refresh(resume)
    return ResumeOut.model_validate(resume)


@router.get("", response_model=list[ResumeOut])
def list_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ResumeOut]:
    records = (
        db.query(Resume)
        .filter(Resume.user_id == current_user.id)
        .order_by(Resume.created_at.desc())
        .all()
    )
    return [ResumeOut.model_validate(item) for item in records]


@router.get("/{resume_id}", response_model=ResumeOut)
def get_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ResumeOut:
    resume = (
        db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == current_user.id).first()
    )
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return ResumeOut.model_validate(resume)
