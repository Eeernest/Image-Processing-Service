from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis, ConnectionPool

from app.core.config import settings

pool = ConnectionPool.from_url(settings.REDIS_URL, decode_responses=True)

async def get_redis():
  client = Redis.from_pool(pool)

  try:
    yield client

  finally:
    await client.close()

RedisDep = Annotated[Redis, Depends(get_redis)]