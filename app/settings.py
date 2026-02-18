import os
from datetime import timedelta
from typing import Final

db_url = os.environ.get("DB_URL", "sqlite://:memory:")

# Basic auth/JWT settings following FastAPI security guide
SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Default scopes for newly created users
DEFAULT_USER_SCOPES: Final[list[str]] = ["users:read", "users:me"]

# Scope required to manage other users' scopes
ADMIN_SCOPES_SCOPE: Final[str] = "admin:scopes"


def access_token_expires_delta() -> timedelta:
    return timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

