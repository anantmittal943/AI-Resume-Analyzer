# AI Resume Analyzer

AI Resume Analyzer is a production-oriented monorepo that compares resumes with job descriptions and returns a suitability score, strengths, gaps, and keyword-level matching details.

## Stack
- Backend: FastAPI, SQLAlchemy, JWT authentication
- Frontend: React + TypeScript + Vite
- Database: PostgreSQL (Docker), SQLite fallback for local backend-only runs
- AI providers: Gemini free tier primary, Groq fallback
- DevOps: Docker, Docker Compose, GitHub Actions CI workflows

## Key Features
- Resume upload support for PDF and DOCX
- Job description management
- AI-assisted suitability scoring with structured output
- Strengths, gaps, and keyword breakdown insights
- User authentication and per-user analysis history
- Text-based operational logging format

## Repository Layout
- backend: FastAPI API, business logic, persistence, tests
- frontend: React UI, API client, tests
- .github/workflows: CI, security checks, Docker validation, release draft
- docs: Architecture and API details

## Quick Start (Docker)
1. Copy .env.example values into your environment as needed.
2. Provide GEMINI_API_KEY and optionally GROQ_API_KEY.
3. Run:

```bash
docker compose up --build
```

If port 8080 is already in use, set a different host port first:

```bash
# PowerShell
$env:FRONTEND_PORT = "8081"
docker compose up --build
```

4. Open:
- Frontend: http://localhost:8080 (or your configured FRONTEND_PORT)
- Backend docs: http://localhost:8000/docs

## Quick Start (Without Docker)

### Backend
1. Create virtual environment and activate it.
2. Install dependencies:

```bash
cd backend
pip install -r requirements-dev.txt
```

3. Create backend/.env from backend/.env.example.
4. Start API:

```bash
uvicorn app.main:app --reload
```

### Frontend
1. Install dependencies:

```bash
cd frontend
npm install
```

2. Create frontend/.env from frontend/.env.example.
3. Start UI:

```bash
npm run dev
```

## Quality Gates

### Backend
```bash
cd backend
ruff check app tests
black --check app tests
mypy app
pytest --cov=app --cov-report=term-missing
```

### Frontend
```bash
cd frontend
npm run lint
npm run test
npm run build
```

## Security and Reliability Practices
- Password complexity enforcement
- JWT access and refresh token flow
- File signature and extension validation
- Ownership checks on every user resource
- Dependency security audits in CI
- Docker build validation in CI

## CI/CD Scope
- CI implemented with strict build/test checks on pull requests and main pushes
- Security workflows included (CodeQL + dependency audits)
- Release workflow creates draft releases on semantic version tags
- Automatic cloud deployment intentionally excluded for now

## Suggested Branch Protection Rules
- Require pull request reviews
- Require all CI workflows to pass before merge
- Dismiss stale approvals on new commits

## License
MIT
