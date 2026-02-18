from datetime import datetime, timezone
from typing import Annotated

import bcrypt
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt

from app.crud import get_user_by_username
from app.models import User
from app.schemas import TokenData
from app.settings import (
    ADMIN_SCOPES_SCOPE,
    ALGORITHM,
    SECRET_KEY,
    access_token_expires_delta,
)

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/token",
    scopes={
        "users:read": "Read users data.",
        "users:me": "Read current user profile.",
        ADMIN_SCOPES_SCOPE: "Manage user scopes.",
    },
)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


async def authenticate_user(username: str, password: str):
    user = await get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(
    data: dict, scopes: list[str] | None = None, expires_delta=None
) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or access_token_expires_delta()
    )
    to_encode.update({"exp": expire, "scopes": scopes or []})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    security_scopes: SecurityScopes,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    authenticate_value = (
        f'Bearer scope="{security_scopes.scope_str}"'
        if security_scopes.scopes
        else "Bearer"
    )
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        token_scopes: list[str] = payload.get("scopes", [])
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username, scopes=token_scopes)
    except JWTError:
        raise credentials_exception

    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )

    user = await get_user_by_username(token_data.username)  # type: ignore[arg-type]
    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated"
        )

    return user


async def get_current_active_user(current_user=Security(get_current_user)) -> User:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_admin_user(
    current_user=Security(get_current_user, scopes=[ADMIN_SCOPES_SCOPE]),
) -> User:
    return current_user
