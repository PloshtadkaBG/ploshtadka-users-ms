from uuid import UUID

from ms_core import CRUD

from app.models import User
from app.schemas import Schema

user_crud = CRUD(User, Schema)


async def get_user_by_username(username: str) -> User | None:
    return await User.get_or_none(username=username)


async def get_user_by_email(email: str) -> User | None:
    return await User.get_or_none(email=email)


async def get_user_by_google_id(google_id: str) -> User | None:
    return await User.get_or_none(google_id=google_id)


async def get_user_by_id(user_id: UUID) -> User | None:
    return await User.get_or_none(id=user_id)


async def create_user(
    username: str,
    email: str | None,
    full_name: str | None,
    hashed_password: str | None,
    scopes: list[str] | None = None,
    google_id: str | None = None,
) -> User:
    return await User.create(
        username=username,
        email=email,
        full_name=full_name,
        hashed_password=hashed_password,
        scopes=scopes or [],
        google_id=google_id,
    )


async def get_users_by_ids(ids: list[UUID]) -> list[User]:
    return await User.filter(id__in=ids).all()


async def update_user_scopes(user_id: UUID, scopes: list[str]) -> User | None:
    user = await User.get_or_none(id=user_id)
    if not user:
        return None
    user.scopes = scopes
    await user.save()
    return user
