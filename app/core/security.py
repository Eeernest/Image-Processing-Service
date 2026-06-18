from fastapi.concurrency import run_in_threadpool
import jwt
from pwdlib import PasswordHash

class Security:
  def __init__(self):
    self.hasher = PasswordHash.recommended()

  async def get_password_hash(self, password: str) -> str:
    return await run_in_threadpool(self.hasher.hash, password)
  
  async def verify_password(self, password: str, hashed_password: str) -> str:
    return await run_in_threadpool(self.hasher.verify, password, hashed_password)
  
  def encode_jwt(self, to_encode: dict, secret_key: str, algorithm: str) -> str:
    return jwt.encode(to_encode, secret_key, algorithm)