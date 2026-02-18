from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr
from tortoise import Tortoise
from tortoise.contrib.pydantic import pydantic_model_creator

from app.models import User

Tortoise.init_models(["app.models"], "models")

Schema = pydantic_model_creator(User, name="UserRead", exclude=("hashed_password",))
Create = pydantic_model_creator(User, name="UserCreateDB", exclude_readonly=True)


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    full_name: str | None = None
    email: EmailStr | None = None
    is_active: bool = True
    scopes: list[str] = []


class UserCreate(UserBase):
    password: str


class UserPublic(UserBase):
    id: UUID


class UserUpdate(BaseModel):
    username: str | None = None
    full_name: str | None = None
    password: str | None = None
    email: EmailStr | None = None
    is_active: bool | None = None


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []


class UserScopesUpdate(BaseModel):
    scopes: list[str]
