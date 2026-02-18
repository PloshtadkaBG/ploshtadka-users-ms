from fastapi import APIRouter, Security

from app.deps import get_current_admin_user
from app.settings import ADMIN_SCOPES_SCOPE, DEFAULT_USER_SCOPES

router = APIRouter(prefix="/scopes", tags=["scopes"])


@router.get("/", response_model=list[str])
async def list_all_scopes(current_admin=Security(get_current_admin_user)) -> list[str]:
    """
    List all known scopes in the system.

    Currently these are composed from:
    - default user scopes
    - admin scopes management scope
    """
    scopes = set(DEFAULT_USER_SCOPES)
    scopes.add(ADMIN_SCOPES_SCOPE)
    return sorted(scopes)
