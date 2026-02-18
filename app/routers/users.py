from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Path, Security, status

from app import Schema, user_crud
from app.auth import get_password_hash
from app.crud import (
    create_user,
    get_user_by_email,
    get_user_by_id,
    get_user_by_username,
    update_user_scopes,
)
from app.deps import (
    get_current_active_user,
    get_current_admin_user,
    require_scopes,
)
from app.models import User
from app.schemas import UserCreate, UserPublic, UserScopesUpdate
from app.settings import DEFAULT_USER_SCOPES

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserCreate) -> UserPublic:
    existing_username = await get_user_by_username(payload.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    if payload.email:
        existing_email = await get_user_by_email(str(payload.email))
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered",
            )

    hashed_password = get_password_hash(payload.password)
    user = await create_user(
        username=payload.username,
        email=str(payload.email) if payload.email else None,
        full_name=payload.full_name,
        hashed_password=hashed_password,
        scopes=DEFAULT_USER_SCOPES,
    )
    return UserPublic.model_validate(user)


@router.get("/", response_model=list[Schema])
async def list_users(
    _=Depends(require_scopes("users:read")),
) -> list[Schema]:
    return await user_crud.get_all()


@router.get("/{user_id}", response_model=Schema)
async def get_user(user_id: UUID = Path()) -> Schema | None:
    return await user_crud.get_by_id(user_id)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    _=Security(get_current_admin_user), user_id: UUID = Path()
) -> None:
    await user_crud.delete_by(id=user_id)


@router.get("/@me/get", response_model=UserPublic)
async def read_users_me(
    current_user: User = Security(get_current_active_user),
) -> UserPublic:
    return UserPublic.model_validate(current_user)


@router.get("/{user_id}/scopes", response_model=UserScopesUpdate, tags=["admin"])
async def get_user_scopes(
    user_id: UUID = Path(),
    current_admin=Security(get_current_admin_user),
) -> UserScopesUpdate:
    user = await get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return UserScopesUpdate(scopes=user.scopes or [])


@router.put("/{user_id}/scopes", response_model=UserScopesUpdate, tags=["admin"])
async def set_user_scopes(
    user_id: UUID,
    payload: UserScopesUpdate,
    current_admin=Security(get_current_admin_user),
) -> UserScopesUpdate:
    user = await update_user_scopes(user_id, payload.scopes)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return UserScopesUpdate(scopes=user.scopes or [])
