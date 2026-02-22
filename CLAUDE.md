# CLAUDE.md — ploshtadka-users-ms

FastAPI microservice that is the **auth authority** for the entire PloshtadkaBG platform. It issues JWTs, validates them for Traefik's `forwardAuth`, and owns all user and scope management.

## Package management

Always use `uv`. Never use `pip` directly.

```bash
uv add <package>       # add dependency
uv sync                # install from lockfile
uv run <command>       # run in the venv
```

## Running

```bash
uv run pytest                                                     # run tests
uv run uvicorn main:application --host 0.0.0.0 --port 8000       # dev server
```

## Architecture

### Technology Stack

- **API Framework**: FastAPI + Uvicorn (port 8000)
- **Database**: PostgreSQL with Tortoise ORM and Aerich migrations
- **JWT**: `python-jose` (HS256), bcrypt for password hashing
- **Testing**: pytest with `monkeypatch` and `dependency_overrides`

### Auth role — critical distinction from other services

**This service IS the JWT issuer and validator.** It is the only service that validates JWTs.

- `POST /auth/token` — issues a JWT from credentials
- `GET /auth/verify` — called by Traefik `forwardAuth` for every protected request; decodes and validates the JWT, then returns `X-User-Id`, `X-Username`, `X-User-Scopes` headers to Traefik

`get_current_user()` in `app/deps.py` validates the JWT using `python-jose`. Do **not** remove this validation — it is the gateway check for the entire system.

Downstream services (venues-ms, bookings-ms) do **not** validate JWTs — they only read the headers Traefik injects after this service approves the request.

## Project structure

```
app/
  auth.py              # JWT creation/verification, bcrypt helpers
  crud.py              # user_crud (CRUD instance) + standalone helpers
  deps.py              # get_current_user() (JWT validation), get_current_active_user, get_current_admin_user, require_scopes()
  models.py            # User Tortoise model
  schemas.py           # UserCreate, UserPublic, UserUpdate, UserScopesUpdate, Token, TokenData
  scopes.py            # UserScope, VenueScope, BookingScope StrEnums + DEFAULT_*_SCOPES
  settings.py          # DB_URL, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
  routers/
    auth.py            # POST /auth/token, GET /auth/verify
    users.py           # /users CRUD + GET /@me/get + scopes endpoints
    scopes.py          # GET /scopes/ (admin only)
tests/
  test_users_auth.py   # monkeypatch-based tests, DummyUser, dependency_overrides
```

## Scopes

This service is the **central scope registry** for the whole platform. `app/scopes.py` defines all scopes across all microservices:

| Scope group | StrEnum class | Super-scope |
|---|---|---|
| Users | `UserScope` | `admin:users` |
| Venues | `VenueScope` | `admin:venues` |
| Bookings | `BookingScope` | `admin:bookings` |

### Default scope sets assigned on registration

| Set | Assigned to | Contents |
|---|---|---|
| `DEFAULT_USER_SCOPES` | Regular user | `users:me`, `venues:read`, `bookings:read`, `bookings:write`, `bookings:cancel` |
| `DEFAULT_OWNER_SCOPES` | Venue owner | + `venues:me/write/delete/images/schedule`, `bookings:manage` |
| `DEFAULT_ADMIN_SCOPES` | Admin | `admin:users`, `admin:venues`, `admin:bookings` |

## Authorization patterns

```python
# Any authenticated user
Depends(get_current_active_user)

# Admin only
Security(get_current_admin_user)

# Custom scope check
Depends(require_scopes("users:read"))
```

`require_scopes(*scopes)` is a factory that returns a dependency; it checks `current_user.scopes` directly (not the JWT — the user object is loaded from DB).

## Testing conventions

- **No conftest.py** — fixtures are defined inline in the test file
- Use `DummyUser` (plain class, not Tortoise model) to represent auth'd users
- Use `application.dependency_overrides` to replace `get_current_active_user` / `get_current_admin_user`
- Use `monkeypatch.setattr(router_module, "function_name", fake_async_fn)` to mock CRUD calls — no `AsyncMock`/`patch` needed
- Tests run against SQLite in-memory (default `DB_URL`)

```python
# Typical pattern
def test_something(monkeypatch, client: TestClient):
    from app.routers import users as users_router

    async def fake_get_user_by_username(username: str):
        return None

    monkeypatch.setattr(users_router, "get_user_by_username", fake_get_user_by_username)
    resp = client.post("/users/", json={...})
    assert resp.status_code == 201
```

## Database

- Tests: SQLite in-memory (default)
- Production: PostgreSQL (`DB_URL` env var)
- Migrations: Aerich — config in `pyproject.toml`, stored in `./migrations/`

```bash
uv run aerich migrate --name <description>
uv run aerich upgrade
```

## Environment variables

| Variable | Default | Description |
|---|---|---|
| `DB_URL` | `sqlite://:memory:` | Database connection string |
| `SECRET_KEY` | `change-me-in-production` | JWT signing key — **must** be set in prod |
| `ALGORITHM` | `HS256` | JWT signing algorithm (hardcoded, not overridable) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | JWT TTL |
