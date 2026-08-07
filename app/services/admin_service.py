import app.core.exceptions as e
from app.models.account_model import Account
from app.repositories.account_db_repository import AccountDbRepository

class AdminService:
  def __init__(self, db_repo: AccountDbRepository):
    self.db_repo = db_repo

  async def view_all_accounts(self, is_active: bool | None = None, is_deleted: bool | None = None) -> list[Account]:
    return await self._try_get_all_accounts(is_active, is_deleted)


  async def _try_get_all_accounts(self, is_active: bool | None = None, is_deleted: bool | None = None) -> list[Account]:
    account_obj_list = await self.db_repo.get_all_accounts(is_active, is_deleted)

    if len(account_obj_list) == 0:
      raise e.UserNotFoundException()

    return account_obj_list