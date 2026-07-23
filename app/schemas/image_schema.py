from pydantic import BaseModel, ConfigDict

class ImageBase(BaseModel):
  filename: str

class ImageRead(ImageBase):
  file_size_bytes: int
  id: int

  model_config = ConfigDict(from_attributes=True)