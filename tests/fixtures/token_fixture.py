import uuid

import pytest

from app.core.config import settings
from app.repositories.token_redis_repository import TokenRedisRepository

@pytest.fixture()
def token_redis_repo(redis_container):
  return TokenRedisRepository(redis_container)

@pytest.fixture()
def refresh_token_data() -> dict:
  return {
      "sub": "1",
      "exp": settings.REFRESH_TOKEN_EXPIRE_DAYS,
      "jti": str(uuid.uuid4()),
      "refresh": True
  }