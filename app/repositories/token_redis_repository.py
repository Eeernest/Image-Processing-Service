from redis.asyncio import Redis

class TokenRedisRepository:
  def __init__(self, client: Redis):
    self.client = client

  async def save(self, jti: str, expires_delta: int, account_id: str) -> None:
    await self.client.setex(name=f"refresh_token:{jti}", time=expires_delta, value=account_id)