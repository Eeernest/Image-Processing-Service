from datetime import datetime, timedelta, timezone
import uuid

from fastapi.concurrency import run_in_threadpool
from fastapi.security import OAuth2PasswordBearer
import jwt
from pwdlib import PasswordHash

from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Security:
  def __init__(self):
    self.hasher = PasswordHash.recommended()

  async def get_password_hash(self, password: str) -> str:
    return await run_in_threadpool(self.hasher.hash, password)
  
  async def verify_password(self, password: str, hashed_password: str) -> bool:
    return await run_in_threadpool(self.hasher.verify, password, hashed_password)

  def create_access_token(self, account_data: dict, expires_delta: timedelta | None = None) -> str:
    payload = {
      "sub": account_data.get("sub"),
      "role": account_data.get("role"),
      "exp": self._get_exp_minutes(expires_delta),
      "jti": str(uuid.uuid4()),
      "refresh": False
    }

    token = jwt.encode(payload, settings.SECRET_KEY, settings.ALGORITHM)

    return token

  def create_refresh_token(self, account_data: dict, expires_delta: timedelta | None = None) -> str:
      payload = {
        "sub": account_data.get("sub"),
        "exp": self._get_exp_days(expires_delta),
        "jti": str(uuid.uuid4()),
        "refresh": True
      }
  
      token = jwt.encode(payload, settings.SECRET_KEY, settings.ALGORITHM)
  
      return token

  def decode_jwt(self, token: str) -> dict:
    try:
      return jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)

    # lateron delete this try except and do it in service

    except jwt.PyJWTError as exc:
      raise exc


  def _get_exp_minutes(self, expires_delta: timedelta | None) -> datetime:
    if expires_delta is None:
      expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    return datetime.now(timezone.utc) + expires_delta

  def _get_exp_days(self, expires_delta: timedelta | None) -> datetime:
    if expires_delta is None:
      expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

    return datetime.now(timezone.utc) + expires_delta