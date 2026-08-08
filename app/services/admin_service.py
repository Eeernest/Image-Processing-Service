from sqlalchemy.exc import IntegrityError

import app.core.exceptions as e
from app.models.account_model import Account
from app.repositories.account_db_repository import AccountDbRepository

class AdminService:
  def __init__(self, db_repo: AccountDbRepository):
    self.db_repo = db_repo

  async def view_all_accounts(self, offset: int, limit: int, is_active: bool | None = None, is_deleted: bool | None = None) -> list[Account]:
    return await self._try_get_all_accounts(offset, limit, is_active, is_deleted)

  async def delete_account(self, id: int) -> None:
    account_obj = await self._try_get_account_by_id(id)

    deleted_account_obj = self._try_soft_delete_account(account_obj)

    return await self._try_save_account(deleted_account_obj)



  async def _try_get_all_accounts(self, offset: int, limit: int, is_active: bool | None = None, is_deleted: bool | None = None) -> list[Account]:
    account_obj_list = await self.db_repo.get_all_accounts(offset, limit, is_active, is_deleted)

    if len(account_obj_list) == 0:
      raise e.UserNotFoundException()

    return account_obj_list

  async def _try_get_account_by_id(self, id: int) -> Account:
    account_obj = await self.db_repo.get_by_id(id)

    if account_obj is None:
      raise e.UserNotFoundException()

    return account_obj

  async def _try_save_account(self, account_obj: Account) -> Account:
    try:
      return await self.db_repo.save(account_obj)

    except IntegrityError:
      raise e.FailedToSaveException()



  def _try_soft_delete_account(self, account_obj: Account) -> Account:
    if account_obj.is_deleted == True:
      raise e.AlreadyDeletedException()

    account_obj.is_deleted = True

    return account_obj