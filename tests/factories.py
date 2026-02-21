"""
All test-data builders in one place.
Import from here in every test file — never define dummy data inline.
"""

from __future__ import annotations

from uuid import UUID, uuid4

from app.scopes import DEFAULT_ADMIN_SCOPES, DEFAULT_USER_SCOPES

# ---------------------------------------------------------------------------
# Stable IDs
# ---------------------------------------------------------------------------

USER_ID: UUID = uuid4()
ADMIN_ID: UUID = uuid4()
OTHER_USER_ID: UUID = uuid4()


# ---------------------------------------------------------------------------
# DummyUser — plain class standing in for the Tortoise User model in tests
# ---------------------------------------------------------------------------


class DummyUser:
    def __init__(
        self,
        user_id: UUID | None = None,
        username: str = "user",
        full_name: str | None = None,
        email: str | None = None,
        is_active: bool = True,
        scopes: list | None = None,
    ) -> None:
        self.id = user_id or uuid4()
        self.username = username
        self.full_name = full_name
        self.email = email
        self.is_active = is_active
        self.scopes = list(scopes) if scopes is not None else []


# ---------------------------------------------------------------------------
# User factories
# ---------------------------------------------------------------------------


def make_user(
    user_id: UUID = USER_ID,
    scopes: list | None = None,
) -> DummyUser:
    """Regular user with default user scopes."""
    return DummyUser(
        user_id=user_id,
        username=f"user_{user_id}",
        email=f"user_{user_id}@example.com",
        scopes=scopes if scopes is not None else list(DEFAULT_USER_SCOPES),
    )


def make_admin(user_id: UUID = ADMIN_ID) -> DummyUser:
    """Admin user with default admin scopes."""
    return DummyUser(
        user_id=user_id,
        username="admin",
        email="admin@example.com",
        scopes=list(DEFAULT_ADMIN_SCOPES),
    )


# ---------------------------------------------------------------------------
# Response dict factories
# ---------------------------------------------------------------------------


def user_response(**overrides) -> dict:
    base = dict(
        id=str(USER_ID),
        username=f"user_{USER_ID}",
        email=f"user_{USER_ID}@example.com",
        full_name=None,
        is_active=True,
        scopes=list(DEFAULT_USER_SCOPES),
    )
    return {**base, **overrides}
