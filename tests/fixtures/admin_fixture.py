from unittest.mock import AsyncMock

import pytest

from app.models.account_model import Account, AccountRole
from app.services.admin_service import AdminService

@pytest.fixture()
def mock_admin_db_repo():
  return AsyncMock()

@pytest.fixture()
def admin_service(mock_admin_db_repo):
  return AdminService(mock_admin_db_repo)

@pytest.fixture()
def mock_admin_account_list() -> list:
  return [
    Account(
      id=1,
      username="user1",
      email="user1@example.com",
      hashed_password="Hased_password",
      user_role=AccountRole.user,
      is_active=True,
      is_deleted=False
    ),
    Account(
      id=2,
      username="user2",
      email="user2@example.com",
      hashed_password="Hased_password",
      user_role=AccountRole.admin,
      is_active=False,
      is_deleted=False
    ),
    Account(
      id=3,
      username="user3",
      email="user3@example.com",
      hashed_password="Hased_password",
      user_role=AccountRole.user,
      is_active=True,
      is_deleted=False
    ),
  ]