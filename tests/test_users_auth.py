from uuid import UUID, uuid4

import pytest
from fastapi.testclient import TestClient

from app.settings import ADMIN_SCOPES_SCOPE, DEFAULT_USER_SCOPES


class DummyUser:
    def __init__(
        self,
        user_id: UUID = uuid4(),
        username: str = "user",
        full_name: str | None = None,
        email: str | None = None,
        is_active: bool = True,
        scopes: list[str] | None = None,
    ) -> None:
        self.id = user_id
        self.username = username
        self.full_name = full_name
        self.email = email
        self.is_active = is_active
        self.scopes = scopes or []


@pytest.fixture
def client():
    """
    FastAPI TestClient with auth dependencies overridden, following FastAPI's
    testing patterns (using dependency_overrides).
    """
    from app.deps import get_current_active_user, get_current_admin_user
    from main import application

    def override_active_user():
        return DummyUser(
            user_id=uuid4(),
            username="active-user",
            email="active@example.com",
            scopes=DEFAULT_USER_SCOPES,
        )

    def override_admin_user():
        return DummyUser(
            user_id=uuid4(),
            username="admin",
            email="admin@example.com",
            scopes=[ADMIN_SCOPES_SCOPE],
        )

    application.dependency_overrides[get_current_active_user] = override_active_user
    application.dependency_overrides[get_current_admin_user] = override_admin_user

    with TestClient(application) as test_client:
        yield test_client

    application.dependency_overrides.clear()


def test_login_for_access_token_success(monkeypatch, client: TestClient):
    """
    Test the /auth/token endpoint using a mocked authenticate_user,
    similar to how FastAPI docs mock dependencies in tests.
    """
    from app.routers import auth as auth_router

    dummy_user = DummyUser(
        user_id=uuid4(),
        username="alice",
        email="alice@example.com",
        scopes=DEFAULT_USER_SCOPES,
    )

    async def fake_authenticate_user(username: str, password: str):
        assert username == "alice"
        assert password == "secret"
        return dummy_user

    monkeypatch.setattr(auth_router, "authenticate_user", fake_authenticate_user)

    response = client.post(
        "/auth/token",
        data={"username": "alice", "password": "secret"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    body = response.json()
    assert "access_token" in body
    assert body["token_type"] == "bearer"


def test_register_user_success(monkeypatch, client: TestClient):
    """
    Test POST /users/ with mocked CRUD functions so no real database is used.
    """
    from app.routers import users as users_router

    created_users: list[DummyUser] = []

    async def fake_get_user_by_username(username: str):
        return None

    async def fake_get_user_by_email(email: str):
        return None

    async def fake_create_user(
        username: str,
        email: str | None,
        full_name: str | None,
        hashed_password: str,
        scopes: list[str] | None = None,
    ):
        user = DummyUser(
            user_id=uuid4(),
            username=username,
            full_name=full_name,
            email=email,
            scopes=scopes or [],
        )
        created_users.append(user)
        return user

    monkeypatch.setattr(users_router, "get_user_by_username", fake_get_user_by_username)
    monkeypatch.setattr(users_router, "get_user_by_email", fake_get_user_by_email)
    monkeypatch.setattr(users_router, "create_user", fake_create_user)

    payload = {
        "username": "newuser",
        "password": "strongpassword",
        "email": "newuser@example.com",
        "full_name": "New User",
    }
    response = client.post("/users/", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["username"] == "newuser"
    assert body["email"] == "newuser@example.com"
    assert body["is_active"] is True
    assert created_users
    assert "users:read" in created_users[0].scopes


def test_list_all_scopes_as_admin(client: TestClient):
    """
    Test /scopes/ listing, using the overridden admin dependency.
    """
    response = client.get("/scopes/")
    assert response.status_code == 200
    scopes = response.json()
    assert "users:read" in scopes
    assert "users:me" in scopes
    assert ADMIN_SCOPES_SCOPE in scopes


def test_get_and_set_user_scopes_admin(monkeypatch, client: TestClient):
    """
    Test the admin scopes CRUD endpoints for a given user, with fake CRUD functions.
    """
    from app.routers import users as users_router

    # Shared dummy user object
    stored_user = DummyUser(
        user_id=uuid4(), username="scoped-user", scopes=["users:read"]
    )

    async def fake_get_user_by_id(user_id: int):
        if user_id == stored_user.id:
            return stored_user
        return None

    async def fake_update_user_scopes(user_id: int, scopes: list[str]):
        if user_id != stored_user.id:
            return None
        stored_user.scopes = scopes
        return stored_user

    monkeypatch.setattr(users_router, "get_user_by_id", fake_get_user_by_id)
    monkeypatch.setattr(users_router, "update_user_scopes", fake_update_user_scopes)

    # GET existing scopes
    get_response = client.get(f"/users/{stored_user.id}/scopes")
    assert get_response.status_code == 200
    assert get_response.json() == {"scopes": ["users:read"]}

    # PUT updated scopes
    new_scopes = {"scopes": ["users:read", ADMIN_SCOPES_SCOPE]}
    put_response = client.put(f"/users/{stored_user.id}/scopes", json=new_scopes)
    assert put_response.status_code == 200
    assert put_response.json() == new_scopes
    assert stored_user.scopes == new_scopes["scopes"]
