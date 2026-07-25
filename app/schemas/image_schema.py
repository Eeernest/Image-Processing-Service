from enum import Enum

from pydantic import BaseModel, ConfigDict

class ImageBase(BaseModel):
  filename: str

class ImageRead(ImageBase):
  file_size_bytes: int
  id: int

  model_config = ConfigDict(from_attributes=True)

class ImageFormat(str, Enum):
  PNG = "PNG"
  JPEG = "JPEG"
  WEBP = "WEBP"