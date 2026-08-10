from sqlalchemy.exc import IntegrityError

import app.core.exceptions as e
from app.core.security import Security
from app.models.account_model import Account
from app.repositories.account_db_repository import AccountDbRepository
from app.schemas.account_schema import AccountCreate

class AccountService:
  def __init__(self, security: Security, db_repo: AccountDbRepository):
    self.security = security
    self.db_repo = db_repo

  async def create_account(self, account_data: AccountCreate) -> Account:
    await self._check_username(account_data.username)

    await self._check_email(account_data.email)

    hashed_password = await self.security.get_password_hash(account_data.password)
    
    account_obj = Account(
      username=account_data.username,
      email=account_data.email,
      hashed_password=hashed_password
    )

    return await self._try_save(account_obj)



  async def _check_username(self, username: str) -> None:
    if await self.db_repo.get_by_username(username) is not None:
      raise e.UsernameUnavailableException()

  async def _check_email(self, email: str) -> None:
    if await self.db_repo.get_by_email(email) is not None:
      raise e.EmailUnavailableException()

  async def _try_save(self, account_obj: Account) -> Account:
    try:
      return await self.db_repo.save(account_obj)

    except IntegrityError as exc:
      if "username" in str(exc.orig):
        raise e.UsernameUnavailableException()

      if "email" in str(exc.orig):
        raise e.EmailUnavailableException()

    raise e.AppBaseException()