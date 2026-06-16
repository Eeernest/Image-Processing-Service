from typing import Annotated

from fastapi import Depends

from app.core.security import Security
from app.db.database import SessionDep
from app.repositories.account_repository import AccountDbRepository
from app.services.account_service import AccountService

def get_account_service(session: SessionDep):
  security = Security()
  db_repo = AccountDbRepository(session)

  return AccountService(security, db_repo)

AccountServiceDep = Annotated[AccountService, Depends(get_account_service)]