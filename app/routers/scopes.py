from fastapi import APIRouter, Security

from app.deps import get_current_admin_user
from app.scopes import SCOPE_DESCS

router = APIRouter(prefix="/scopes", tags=["scopes"])


@router.get("/", response_model=list[str])
async def list_all_scopes(_=Security(get_current_admin_user)) -> list[str]:
    """
    List all known scopes in the system.

    Currently these are composed from:
    - default user scopes
    - admin scopes management scope
    """
    return sorted(SCOPE_DESCS.keys())
