from sqlalchemy.exc import IntegrityError

from app.core.exceptions import AppBaseException, UsernameUnavailableException, EmailUnavailableException
from app.core.security import Security
from app.models.account_model import Account
from app.repositories.account_db_repository import AccountDbRepository
from app.schemas.account_schema import AccountCreate

class AccountService:
  def __init__(self, security: Security, db_repo: AccountDbRepository):
    self.security = security
    self.db_repo = db_repo

  async def create_account(self, account_data: AccountCreate) -> Account:
    if await self.db_repo.get_by_username(account_data.username) is not None:
      raise UsernameUnavailableException(f"Username '{account_data.username}' is already in use")
    
    if await self.db_repo.get_by_email(account_data.email) is not None:
      raise EmailUnavailableException(f"Email '{account_data.email}' is already in use")
    
    hashed_password = await self.security.get_password_hash(account_data.password)

    account_obj = Account(
      username=account_data.username,
      email=account_data.email,
      hashed_password=hashed_password
    )

    try:
      return await self.db_repo.save(account_obj)

    except IntegrityError as exc:
      if "username" in str(exc.orig):
        raise UsernameUnavailableException(f"Username '{account_data.username}' is already in use")
      
      if "email" in str(exc.orig):
        raise EmailUnavailableException(f"Email '{account_data.email}' is already in use")
    
    return AppBaseException("Failed to create account")