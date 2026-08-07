from typing import Annotated

from fastapi import Depends

from app.db.database import SessionDep
from app.repositories.account_db_repository import AccountDbRepository
from app.services.admin_service import AdminService

def get_admin_service(session: SessionDep):
  db_repo = AccountDbRepository(session)

  return AdminService(db_repo)

AdminServiceDep = Annotated[AdminService, Depends(get_admin_service)]