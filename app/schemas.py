from typing import Optional

from tortoise import Tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
from pydantic import BaseModel, EmailStr

from app.models import User

Tortoise.init_models(
    ["app.models"], "models"
)

Schema = pydantic_model_creator(User, name="UserRead", exclude=("hashed_password",))
Create = pydantic_model_creator(User, name="UserCreateDB", exclude_readonly=True)


class UserBase(BaseModel):
    username: str
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: bool = True


class UserCreate(UserBase):
    password: str


class UserPublic(UserBase):
    id: int


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None

