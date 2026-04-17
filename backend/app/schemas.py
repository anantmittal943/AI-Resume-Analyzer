from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)


class UserLogin(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    is_active: bool
    created_at: datetime


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str = Field(min_length=20)


class ResumeOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    filename: str
    mime_type: str
    file_size: int
    created_at: datetime


class JobCreate(BaseModel):
    title: str = Field(min_length=2, max_length=255)
    company: str | None = Field(default=None, max_length=255)
    description: str = Field(min_length=20, max_length=20000)


class JobOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    company: str | None
    description: str
    created_at: datetime


class KeywordMatch(BaseModel):
    keyword: str
    matched: bool


class AnalysisCreate(BaseModel):
    resume_id: str
    job_id: str


class AnalysisOut(BaseModel):
    id: str
    resume_id: str
    job_id: str
    suitability_score: int = Field(ge=0, le=100)
    summary: str
    strengths: list[str]
    gaps: list[str]
    keyword_breakdown: list[KeywordMatch]
    provider_used: str
    created_at: datetime


class AnalysisHistoryPage(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[AnalysisOut]
