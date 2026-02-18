from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth import authenticate_user, create_access_token, get_current_user
from app.models import User
from app.schemas import Token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.username}, scopes=user.scopes or []
    )
    return Token(access_token=access_token, token_type="bearer")


@router.get("/verify")
async def verify_token(current_user: User = Depends(get_current_user)):
    """Called by Traefik forwardAuth for every protected request."""
    return Response(
        status_code=200,
        headers={
            "X-User-Id": str(current_user.id),
            "X-User-Scopes": " ".join(current_user.scopes),
            "X-Username": current_user.username,
        },
    )
