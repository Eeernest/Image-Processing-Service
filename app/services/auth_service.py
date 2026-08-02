from datetime import timedelta

from app.core.config import settings
from app.core.exceptions import InvalidCredentialsException
from app.core.security import Security
from app.models.account_model import Account
from app.repositories.account_db_repository import AccountDbRepository
from app.schemas.token_schema import TokenBase

class AuthService:
  def __init__(self, security: Security, db_repo: AccountDbRepository):
    self.security = security
    self.db_repo = db_repo
  
  async def login(self, username: str, password: str) -> TokenBase:
    account_obj = await self._authenticate_user(username, password)

    if account_obj is None:
      raise InvalidCredentialsException()

    access_token = self._get_access_token(account_obj.id, account_obj.user_role)
    refresh_token = self._get_refresh_token(account_obj.id)

    return TokenBase(access_token=access_token, refresh_token=refresh_token, token_type="bearer")




  async def _authenticate_user(self, username: str, password: str) -> Account | None:
    account_obj = await self.db_repo.get_by_username(username)

    if account_obj is None:
      await self.security.verify_password(password, settings.DUMMY_HASH)

      return None
    
    is_password_correct = await self.security.verify_password(password, account_obj.hashed_password)

    if is_password_correct is False:
      return None
    
    return account_obj

  def _get_access_token(self, account_id: int, account_role: str) -> str:
    account_data = {
      "sub": str(account_id),
      "role": account_role
    }

    expires_delta_minutes = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    return self.security.create_access_token(account_data, expires_delta_minutes)

  def _get_refresh_token(self, account_id: int) -> str:
    account_data = {
      "sub": str(account_id)
    }

    expires_delta_days = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    return self.security.create_refresh_token(account_data, expires_delta_days)