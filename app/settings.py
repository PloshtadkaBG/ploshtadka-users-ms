import os
from datetime import timedelta

db_url = os.environ.get("DB_URL", "sqlite://:memory:")
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# Basic auth/JWT settings following FastAPI security guide
SECRET_KEY = os.environ.get("SECRET_KEY", "change-me-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


def access_token_expires_delta() -> timedelta:
    return timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
