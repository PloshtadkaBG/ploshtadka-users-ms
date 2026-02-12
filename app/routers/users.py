from typing import List

from fastapi import APIRouter, HTTPException, Path, Security, status

from app import Schema, user_crud
from app.auth import get_current_active_user, get_password_hash
from app.crud import create_user, get_user_by_email, get_user_by_username
from app.schemas import UserCreate, UserPublic

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
    )
    return UserPublic(
        id=user.id,
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        is_active=user.is_active,
    )


@router.get("/", response_model=List[Schema])
async def list_users() -> List[Schema]:
    return await user_crud.get_all()


@router.get("/{user_id}", response_model=Schema)
async def get_user(user_id: int = Path()) -> Schema | None:
    return await user_crud.get_by_id(user_id)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int = Path()) -> None:
    await user_crud.delete_by(id=user_id)


@router.get("/@me/get", response_model=UserPublic)
async def read_users_me(current_user=Security(get_current_active_user)) -> UserPublic:
    return UserPublic(
        id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name,
        email=current_user.email,
        is_active=current_user.is_active,
    )
