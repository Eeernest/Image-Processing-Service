import re

from pydantic import BaseModel, EmailStr, field_validator

from app.core.exceptions import PasswordTooShortException, PasswordNoUppercaseException, PasswordNumberException

class AccountBase(BaseModel):
  username: str
  email: EmailStr

  @field_validator("username")
  def whitespace_username(cls, v: str) -> str:
    return v.strip()
  
  @field_validator("email")
  def lowercase_email(cls, v: str) -> str:
    return v.lower().strip()
  
class AccountCreate(AccountBase):
  password: str

  @field_validator("password")
  def strong_password(cls, v: str) -> str:
    if len(v) < 8:
      raise PasswordTooShortException()
    
    if not re.search(r"[A-Z]", v):
      raise PasswordNoUppercaseException()
    
    if not re.search(r"\d", v):
      raise PasswordNumberException()
    
    return v