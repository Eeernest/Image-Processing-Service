from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import Column, Integer, String, Boolean, DateTime

from app.db.database import Base

class AccountRole(str, Enum):
  user = "user"
  admin = "admin"

class Account:
  __tablename__ = "accounts"

  id = Column(Integer, primary_key=True, index=True)
  username = Column(String, nullable=False, unique=True, index=True)
  email = Column(String, nullable=False, unique=True, index=True)
  hashed_password = Column(String, nullable=False)
  user_role = Column(String, default="user", index=True)
  is_active = Column(Boolean, default=True)
  is_deleted = Column(Boolean, default=False)
  created_at = Column(DateTime, default=datetime.now(timezone.utc))
  updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))