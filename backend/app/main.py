import logging
import time
from contextlib import asynccontextmanager
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.db import init_db
from app.logging_config import setup_logging
from app.routers.analyses import router as analyses_router
from app.routers.auth import router as auth_router
from app.routers.jobs import router as jobs_router
from app.routers.resumes import router as resumes_router

settings = get_settings()
setup_logging(settings.log_level)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    init_db()
    logger.info("Application startup completed", extra={"action": "startup"})
    yield


app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = str(uuid4())
    started = time.perf_counter()
    response = await call_next(request)
    duration_ms = int((time.perf_counter() - started) * 1000)
    logger.info(
        f"{request.method} {request.url.path} -> {response.status_code}",
        extra={"request_id": request_id, "duration_ms": duration_ms},
    )
    response.headers["X-Request-ID"] = request_id
    return response


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.app_env}


app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(resumes_router, prefix=settings.api_v1_prefix)
app.include_router(jobs_router, prefix=settings.api_v1_prefix)
app.include_router(analyses_router, prefix=settings.api_v1_prefix)
