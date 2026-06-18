from typing import Annotated

from fastapi import Depends

from app.core.security import Security
from app.db.database import SessionDep
from app.repositories.account_db_repository import AccountDbRepository
from app.services.auth_service import AuthService

def get_auth_service(session: SessionDep):
  security = Security()
  db_repo = AccountDbRepository(session)

  return AuthService(security, db_repo)

AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]