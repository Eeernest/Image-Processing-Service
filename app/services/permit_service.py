import jwt

import app.core.exceptions as e
from app.core.security import Security
from app.models.account_model import Account
from app.repositories.account_db_repository import AccountDbRepository

class PermitService:
  def __init__(self, security: Security, db_repo: AccountDbRepository):
    self.security = security
    self.db_repo = db_repo

  async def get_current_user(self, encoded_access_token: str) -> Account:
    access_token_data = self._try_decode_jwt(encoded_access_token)

    self._check_token_data(access_token_data)

    return await self._try_get_account_by_id(int(access_token_data["sub"]))



  async def _try_get_account_by_id(self, id: int) -> Account:
    account_obj = await self.db_repo.get_by_id(id)

    if account_obj is None:
      raise e.InvalidTokenException()

    if account_obj.is_active == False:
      raise e.InactiveAccountException()

    if account_obj.is_deleted == True:
      raise e.DeletedAccountException()

    return account_obj



  def _check_token_data(self, access_token_data: dict) -> None:
    if access_token_data["sub"] is None:
      raise e.InvalidTokenException()

    if access_token_data["role"] is None:
      raise e.InvalidTokenException()

  

  def _try_decode_jwt(self, encoded_access_token: str) -> dict:
    try:
      return self.security.decode_jwt(encoded_access_token)

    except jwt.ExpiredSignatureError:
      raise e.TokenExpiredException()

    except jwt.PyJWTError:
      raise e.InvalidTokenException()