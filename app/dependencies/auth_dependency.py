from typing import Annotated

from fastapi import Depends

from app.core.security import Security
from app.db.database import SessionDep
from app.redis.redis_client import RedisDep
from app.repositories.account_db_repository import AccountDbRepository
from app.repositories.token_redis_repository import TokenRedisRepository
from app.services.auth_service import AuthService

def get_auth_service(session: SessionDep, client: RedisDep):
  security = Security()
  db_repo = AccountDbRepository(session)
  redis_repo = TokenRedisRepository(client)

  return AuthService(security, db_repo, redis_repo)

AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]