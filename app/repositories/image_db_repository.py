from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.image_model import Image

class ImageDbRepository:
  def __init__(self, session: AsyncSession):
    self.session = session

  async def save(self, image_obj: Image) -> Image:
    try:
      self.session.add(image_obj)
      await self.session.commit()
      await self.session.refresh(image_obj)

      return image_obj

    except IntegrityError as exc:
      await self.session.rollback()

      raise exc

  async def delete(self, id: int) -> None:
    statement = delete(Image).where(Image.id == id)
    await self.session.execute(statement)
    await self.session.commit()

  async def get_by_id(self, id: int) -> Image | None:
    result = await self.session.execute(select(Image).where(Image.id == id))

    return result.scalar_one_or_none()