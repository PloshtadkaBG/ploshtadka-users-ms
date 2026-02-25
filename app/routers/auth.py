from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger

from app.auth import authenticate_user, create_access_token
from app.cache import get_verify_cache, set_verify_cache
from app.deps import resolve_user
from app.schemas import Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        logger.warning("Failed login attempt for username={}", form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    logger.info("User logged in: username={}", form_data.username)

    access_token = create_access_token(
        data={"sub": user.username}, scopes=user.scopes or []
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/verify")
async def verify_token(request: Request):
    """Called by Traefik forwardAuth for every protected request."""
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth_header[7:]

    cached = await get_verify_cache(token)
    if cached:
        logger.debug("Cache hit for verify: username={}", cached["username"])
        return Response(
            status_code=200,
            headers={
                "X-User-Id": cached["user_id"],
                "X-User-Scopes": cached["scopes"],
                "X-Username": cached["username"],
            },
        )

    user = await resolve_user(token)
    logger.debug("Cache miss for verify: username={}", user.username)
    payload = {
        "user_id": str(user.id),
        "username": user.username,
        "scopes": " ".join(user.scopes or []),
    }
    await set_verify_cache(token, str(user.id), payload)

    return Response(
        status_code=200,
        headers={
            "X-User-Id": payload["user_id"],
            "X-User-Scopes": payload["scopes"],
            "X-Username": payload["username"],
        },
    )
