from uuid import UUID

from ms_core import CRUD

from app.models import User
from app.schemas import Schema

user_crud = CRUD(User, Schema)


async def get_user_by_username(username: str) -> User | None:
    return await User.get_or_none(username=username)


async def get_user_by_email(email: str) -> User | None:
    return await User.get_or_none(email=email)


async def get_user_by_id(user_id: UUID) -> User | None:
    return await User.get_or_none(id=user_id)


async def create_user(
    username: str,
    email: str | None,
    full_name: str | None,
    hashed_password: str,
    scopes: list[str] | None = None,
) -> User:
    return await User.create(
        username=username,
        email=email,
        full_name=full_name,
        hashed_password=hashed_password,
        scopes=scopes or [],
    )


async def update_user_scopes(user_id: UUID, scopes: list[str]) -> User | None:
    user = await User.get_or_none(id=user_id)
    if not user:
        return None
    user.scopes = scopes
    await user.save()
    return user
