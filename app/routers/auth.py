from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
import urllib3
from google.auth.transport import urllib3 as google_urllib3
from google.oauth2 import id_token as google_id_token
from loguru import logger
from pydantic import BaseModel

from app.auth import authenticate_user, create_access_token
from app.cache import get_verify_cache, set_verify_cache
from app.crud import create_user, get_user_by_email, get_user_by_google_id, get_user_by_username
from app.deps import resolve_user
from app.schemas import Token
from app.scopes import DEFAULT_USER_SCOPES
from app.settings import GOOGLE_CLIENT_ID

router = APIRouter(prefix="/auth", tags=["auth"])

_http = urllib3.PoolManager()
_google_request = google_urllib3.Request(_http)


class GoogleTokenRequest(BaseModel):
    credential: str


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


@router.post("/google", response_model=Token)
async def login_with_google(body: GoogleTokenRequest) -> Token:
    """Exchange a Google ID token for a platform JWT."""
    try:
        claims = google_id_token.verify_oauth2_token(
            body.credential, _google_request, GOOGLE_CLIENT_ID
        )
    except Exception as exc:
        logger.warning("Google token verification failed: {}", exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google credential",
        )

    google_sub: str = claims["sub"]
    email: str = claims.get("email", "")
    full_name: str | None = claims.get("name")

    # 1. Look up by google_id first (fastest path for returning users)
    user = await get_user_by_google_id(google_sub)

    if user is None and email:
        # 2. Auto-link: existing account with the same email
        user = await get_user_by_email(email)
        if user is not None:
            user.google_id = google_sub
            await user.save()
            logger.info("Linked Google account to existing user: username={}", user.username)

    if user is None:
        # 3. First-time Google sign-in — create a new account
        username_base = email.split("@")[0] if email else google_sub[:20]
        username = username_base
        counter = 1
        while await get_user_by_username(username) is not None:
            username = f"{username_base}{counter}"
            counter += 1

        user = await create_user(
            username=username,
            email=email or None,
            full_name=full_name,
            hashed_password=None,
            scopes=[str(s) for s in DEFAULT_USER_SCOPES],
            google_id=google_sub,
        )
        logger.info("Created new user via Google OAuth: username={}", user.username)

    access_token = create_access_token(
        data={"sub": user.username}, scopes=user.scopes or []
    )
    return Token(access_token=access_token, token_type="bearer")
