from ms_core import AbstractModel
from tortoise import fields


class User(AbstractModel):
    """
    Basic user model for authentication and CRUD.

    Follows the structure from the FastAPI user/auth guides:
    - unique username (can be changed to email later)
    - hashed password stored in DB
    - is_active flag for soft deactivation
    """

    username = fields.CharField(max_length=128, unique=True)
    full_name = fields.CharField(max_length=256, null=True)
    email = fields.CharField(max_length=256, null=True, unique=True)
    hashed_password = fields.CharField(max_length=256)
    is_active = fields.BooleanField(default=True)
