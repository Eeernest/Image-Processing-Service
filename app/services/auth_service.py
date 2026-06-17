from datetime import datetime, timedelta, timezone

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

  async def _authenticate_user(self, username: str, password: str) -> Account | None:
    account_obj = await self.db_repo.get_by_username(username)

    if account_obj is None:
      await self.security.verify_password(password, settings.DUMMY_HASH)

      return None
    
    is_password_correct = await self.security.verify_password(password, account_obj.hashed_password)

    if is_password_correct is False:
      return None
    
    return account_obj
  
  async def _create_access_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()

    if expires_delta is not None:
      expire = datetime.now(timezone.utc) + expires_delta

    if expires_delta is None:
      expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode.update({"exp": expire})

    encoded_jwt = await self.security.encode_jwt(
      to_encode=to_encode,
      secret_key=settings.SECRET_KEY,
      algorithm=settings.ALGORITHM
    )

    return encoded_jwt
  
  async def login(self, username: str, password: str) -> TokenBase:
    account_obj = await self._authenticate_user(username, password)

    if account_obj is None:
      raise InvalidCredentialsException()
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    access_token = await self._create_access_token(
      data={"sub": str(account_obj.id), "role": account_obj.user_role},
      expires_delta=access_token_expires
    )

    return TokenBase(access_token=access_token, token_type="bearer")