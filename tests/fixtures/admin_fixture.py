from unittest.mock import AsyncMock

from httpx import AsyncClient, ASGITransport
import pytest

from app.dependencies.admin_dependency import get_admin_service
from app.dependencies.permit_dependency import get_current_admin
from app.main import app
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

@pytest.fixture()
def mock_admin_service():
  return AsyncMock()

@pytest.fixture()
def mock_current_admin():
  return Account(
    id=5,
    username="admin",
    email="admin@example.com",
    hashed_password="Hased_password",
    user_role=AccountRole.admin,
    is_active=True,
    is_deleted=False
  )

@pytest.fixture()
async def unit_admin_client(mock_admin_service, mock_current_admin):
  app.dependency_overrides[get_admin_service] = lambda: mock_admin_service
  app.dependency_overrides[get_current_admin] = lambda: mock_current_admin

  async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
    yield c

  app.dependency_overrides.clear()