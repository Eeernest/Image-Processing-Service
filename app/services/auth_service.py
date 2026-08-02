from datetime import timedelta
import uuid

from redis.exceptions import RedisError

from app.core.config import settings
import app.core.exceptions as e
from app.core.security import Security
from app.models.account_model import Account
from app.repositories.account_db_repository import AccountDbRepository
from app.repositories.token_redis_repository import TokenRedisRepository
from app.schemas.token_schema import TokenBase

class AuthService:
  def __init__(self, security: Security, db_repo: AccountDbRepository, redis_repo: TokenRedisRepository):
    self.security = security
    self.db_repo = db_repo
    self.redis_repo = redis_repo
  
  async def login(self, username: str, password: str) -> TokenBase:
    account_obj = await self._authenticate_user(username, password)

    if account_obj is None:
      raise e.InvalidCredentialsException()

    access_token_data = self._get_access_token_data(account_obj.id, account_obj.user_role)
    refresh_token_data = self._get_refresh_token_data(account_obj.id)

    encoded_access_token = self._get_access_token(access_token_data)
    encoded_refresh_token = self._get_refresh_token(refresh_token_data)

    await self._try_store_refresh_token(refresh_token_data["jti"], settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400, refresh_token_data["sub"])

    return TokenBase(access_token=encoded_access_token, refresh_token=encoded_refresh_token, token_type="bearer")




  async def _authenticate_user(self, username: str, password: str) -> Account | None:
    account_obj = await self.db_repo.get_by_username(username)

    if account_obj is None:
      await self.security.verify_password(password, settings.DUMMY_HASH)

      return None
    
    is_password_correct = await self.security.verify_password(password, account_obj.hashed_password)

    if is_password_correct is False:
      return None
    
    return account_obj
  


  def _get_access_token_data(self, account_id: int, account_role: str) -> dict:
    return {
      "sub": str(account_id),
      "role": account_role,
      "jti": str(uuid.uuid4())
    }

  def _get_refresh_token_data(self, account_id: int) -> dict:
    return {
      "sub": str(account_id),
      "jti": str(uuid.uuid4())
    }



  def _get_access_token(self, account_token_data: dict) -> str:

    expires_delta_minutes = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    return self.security.create_access_token(account_token_data, expires_delta_minutes)

  def _get_refresh_token(self, refresh_token_data: dict) -> str:
    expires_delta_days = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    return self.security.create_refresh_token(refresh_token_data, expires_delta_days)



  async def _try_store_refresh_token(self, jti: str, expires_delta_seconds: int, sub: str) -> None:
    try:
      await self.redis_repo.store_refresh_token(jti, expires_delta_seconds, sub)

    except RedisError:
      raise e.RedisFailureException()