from typing import Annotated

from fastapi import Depends

from app.core.security import oauth2_scheme, Security
from app.db.database import SessionDep
from app.models.account_model import Account
from app.repositories.account_db_repository import AccountDbRepository
from app.services.permit_service import PermitService

def get_permit_service(session: SessionDep):
  security = Security()
  db_repo = AccountDbRepository(session)

  return PermitService(security, db_repo)

PermitServiceDep = Annotated[PermitService, Depends(get_permit_service)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]

async def get_current_user(service: PermitServiceDep, encoded_access_token: TokenDep) -> Account:
  return await service.get_current_user(encoded_access_token)

CurrentUserDep = Annotated[Account, Depends(get_current_user)]

async def get_current_admin(service: PermitServiceDep, encoded_access_token: TokenDep) -> Account:
  return await service.get_current_admin(encoded_access_token)

CurrentAdminDep = Annotated[Account, Depends(get_current_admin)]