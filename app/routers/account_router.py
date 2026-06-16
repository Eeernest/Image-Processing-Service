from fastapi import APIRouter

from app.dependencies.account_dependency import AccountServiceDep
from app.schemas.account_schema import AccountCreate, AccountRead

router = APIRouter()

@router.post("/register", response_model=AccountRead)
async def register(service: AccountServiceDep, account_data: AccountCreate):
  return await service.create_account(account_data)