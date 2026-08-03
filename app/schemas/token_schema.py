from pydantic import BaseModel

class TokenBase(BaseModel):
  access_token: str
  refresh_token: str
  token_type: str

class TokenRead(TokenBase):
  pass

class TokenData(BaseModel):
  account_id: int
  user_role: str

class RefreshTokenRequest(BaseModel):
  refresh_token: str