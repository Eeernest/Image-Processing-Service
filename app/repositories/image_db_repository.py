from sqlalchemy.ext.asyncio import AsyncSession

from app.models.image_model import Image

class ImageDbRepository:
  def __init__(self, session: AsyncSession):
    self.session = session

  async def save(self, image_obj: Image) -> Image:
    self.session.add(image_obj)
    await self.session.commit()
    await self.session.refresh(image_obj)

    return image_obj