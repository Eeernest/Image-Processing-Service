from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.database import Base

class UserImage(Base):
  __tablename__ = "user_images"

  id = Column(Integer, primary_key=True, index=True)
  account_id = Column(Integer, ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False, index=True)
  filename = Column(String, nullable=False)
  s3_key = Column(String, nullable=False, unique=True)
  file_format = Column(String, nullable=False)
  file_size_bytes = Column(Integer, nullable=False)
  created_at = Column(DateTime, default=datetime.utcnow)

  account = relationship("Account", back_populates="user_images")