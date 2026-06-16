from fastapi.concurrency import run_in_threadpool
from pwdlib import PasswordHash

class Security:
  def __init__(self):
    self.hasher = PasswordHash.recommended()

  async def get_password_hash(self, password: str) -> str:
    return await run_in_threadpool(self.hasher.hash, password)