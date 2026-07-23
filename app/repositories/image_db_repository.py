from sqlalchemy import select
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

  async def get_by_account_id(self, account_id: int) -> Image | None:
    result = await self.session.execute(select(Image).where(Image.account_id == account_id))

    return result.scalar_one_or_none()

  async def get_by_id(self, id: int) -> Image | None:
    result = await self.session.execute(select(Image).where(Image.id == id))

    return result.scalar_one_or_none()