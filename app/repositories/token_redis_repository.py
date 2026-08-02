from redis.asyncio import Redis

class TokenRedisRepository:
  def __init__(self, client: Redis):
    self.client = client

  async def store_refresh_token(self, jti: str, expires_delta: int, sub: str ) -> None:
    await self.client.setex(self._get_key(jti), expires_delta, sub)

  async def get_account_id(self, jti: str) -> str | None:
    return await self.client.get(self._get_key(jti))

  async def delete_refresh_token(self, jti: str) -> None:
    return await self.client.delete(self._get_key(jti))



  def _get_key(self, jti: str) -> str:
    return f"refresh_token:{jti}"