from ms_core import CRUD

from app.models import User
from app.schemas import Schema

user_crud = CRUD(User, Schema)


async def get_user_by_username(username: str) -> User | None:
    return await User.get_or_none(username=username)


async def get_user_by_email(email: str) -> User | None:
    return await User.get_or_none(email=email)


async def create_user(
    username: str, email: str | None, full_name: str | None, hashed_password: str
) -> User:
    return await User.create(
        username=username,
        email=email,
        full_name=full_name,
        hashed_password=hashed_password,
    )
