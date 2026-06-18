from fastapi import APIRouter

from app.dependencies.permit_dependency import PermitServiceDep, TokenDep
from app.schemas.account_schema import AccountRead

router = APIRouter()

@router.get("/users/me", response_model=AccountRead)
async def read_user_me(service: PermitServiceDep, token: TokenDep):
  return await service.get_current_user(token)