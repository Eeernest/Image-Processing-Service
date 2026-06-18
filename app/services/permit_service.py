from jwt.exceptions import InvalidTokenError

from app.core.config import settings
from app.core.exceptions import InvalidTokenException, InactiveAccountException, DeletedAccountException
from app.core.security import Security
from app.models.account_model import Account
from app.repositories.account_db_repository import AccountDbRepository
from app.schemas.token_schema import TokenData

class PermitService:
  def __init__(self, security: Security, db_repo: AccountDbRepository):
    self.security = security
    self.db_repo = db_repo

  async def get_current_user(self, token: str) -> Account:
    try:
      payload = self.security.decode_jwt(token, settings.SECRET_KEY, settings.ALGORITHM)

      account_id = payload.get("sub")
      user_role = payload.get("role")

      if account_id is None:
        raise InvalidTokenException
      
      token_data = TokenData(account_id=int(account_id), user_role=user_role)

    except InvalidTokenError:
      raise InvalidTokenException
    
    account_obj = await self.db_repo.get_by_id(token_data.account_id)

    if account_obj is None:
      raise InvalidTokenException
    
    if account_obj.is_active == False:
      raise InactiveAccountException
    
    if account_obj.is_deleted == True:
      raise DeletedAccountException
    
    return account_obj