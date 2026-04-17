from datetime import UTC, datetime, timedelta
from typing import Any, cast

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.config import get_settings

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return cast(str, pwd_context.hash(password))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return cast(bool, pwd_context.verify(plain_password, hashed_password))


def create_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    settings = get_settings()
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + expires_delta).timestamp()),
    }
    token = jwt.encode(payload, settings.secret_key, algorithm=settings.jwt_algorithm)
    return cast(str, token)


def create_access_token(subject: str) -> str:
    settings = get_settings()
    return create_token(
        subject=subject,
        token_type=ACCESS_TOKEN_TYPE,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )


def create_refresh_token(subject: str) -> str:
    settings = get_settings()
    return create_token(
        subject=subject,
        token_type=REFRESH_TOKEN_TYPE,
        expires_delta=timedelta(days=settings.refresh_token_expire_days),
    )


def decode_token(token: str, expected_type: str | None = None) -> dict:
    settings = get_settings()
    try:
        payload = cast(
            dict[str, Any],
            jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm]),
        )
    except JWTError as exc:
        raise ValueError("Invalid token") from exc

    token_type = payload.get("type")
    subject = payload.get("sub")
    if not subject:
        raise ValueError("Token missing subject")
    if expected_type and token_type != expected_type:
        raise ValueError("Invalid token type")
    return payload
