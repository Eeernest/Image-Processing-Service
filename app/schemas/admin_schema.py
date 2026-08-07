from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

class AdminRead(BaseModel):
  id: int
  username: str
  email: EmailStr
  user_role: str
  is_active: bool
  is_deleted: bool

  model_config = ConfigDict(from_attributes=True)