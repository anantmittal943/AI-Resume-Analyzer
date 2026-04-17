# Architecture Overview

## High-Level Flow
1. Authenticated user uploads resume (PDF or DOCX).
2. Backend validates and parses file content.
3. User saves a job description.
4. User triggers analysis with selected resume and job entry.
5. Backend evaluates using Gemini primary provider, Groq fallback, and heuristic fallback if needed.
6. Analysis result is persisted and returned to frontend.

## Backend Layers
- Routers: HTTP transport and request validation.
- Services: File parsing and analysis orchestration.
- Providers: External LLM integrations with fallback strategy.
- Models: SQLAlchemy entities for users, resumes, jobs, and analyses.
- Security: JWT token creation/validation and password hashing.

## Frontend Layers
- API client: Typed HTTP access with token persistence.
- Auth panel: Login and registration flow.
- Dashboard: Resume upload, job creation, analysis execution, history display.

## Data Model
- users
- resumes
- jobs
- analyses
- audit_logs

Each table is user-scoped through user_id to enforce data isolation.

## Logging
Backend logs are emitted in text format with pipe-delimited fields to simplify operational tracing.
