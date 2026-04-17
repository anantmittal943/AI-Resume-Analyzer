# API Reference

Base path: /api/v1

## Auth
- POST /auth/register
- POST /auth/login
- POST /auth/refresh
- GET /auth/me

## Resumes
- POST /resumes (multipart file upload)
- GET /resumes
- GET /resumes/{resume_id}

## Jobs
- POST /jobs
- GET /jobs
- GET /jobs/{job_id}

## Analyses
- POST /analyses
- GET /analyses/history?limit=10&offset=0

## Health
- GET /health

## Authentication
Protected endpoints require Authorization header:

Bearer <access_token>
