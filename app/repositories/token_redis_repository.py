from redis.asyncio import Redis

class TokenRedisRepository:
  def __init__(self, client: Redis):
    self.client = client

  async def store_refresh_token(self, jti: str, expires_delta: int, account_id: str ) -> None:
    await self.client.setex(f"refresh_token:{jti}", expires_delta, account_id)

  async def get_refresh_token(self, jti: str) -> str | None:
    return await self.client.get(f"refresh_token:{jti}")