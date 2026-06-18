from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account_model import Account

class AccountDbRepository:
  def __init__(self, session: AsyncSession):
    self.session = session

  async def save(self, account_obj: Account) -> Account:
    try:
      self.session.add(account_obj)
      await self.session.commit()
      await self.session.refresh(account_obj)

      return account_obj
    
    except IntegrityError as exc:
      await self.session.rollback()
      raise exc
    
  async def get_by_username(self, username: str) -> Account | None:
    result = await self.session.execute(select(Account).where(Account.username == username))

    return result.scalar_one_or_none()
  
  async def get_by_email(self, email: str) -> Account | None:
    result = await self.session.execute(select(Account).where(Account.email == email))

    return result.scalar_one_or_none()
  
  async def get_by_id(self, id: int) -> Account | None:
    result = await self.session.execute(select(Account).where(Account.id == id))

    return result.scalar_one_or_none()