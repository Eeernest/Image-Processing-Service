from unittest.mock import AsyncMock, Mock

from httpx import AsyncClient, ASGITransport
import pytest

from app.core.security import oauth2_scheme
from app.dependencies.permit_dependency import get_permit_service
from app.main import app
from app.models.account_model import AccountRole, Account
from app.services.permit_service import PermitService

@pytest.fixture()
def mock_permit_security():
  mock = AsyncMock()
  mock.decode_jwt = Mock()

  return mock

@pytest.fixture()
def mock_permit_db_repo():
  return AsyncMock()

@pytest.fixture()
def permit_service(mock_permit_security, mock_permit_db_repo):
  return PermitService(mock_permit_security, mock_permit_db_repo)

@pytest.fixture()
def permit_account_obj():
  return Account(
    id=1,
    username="user1",
    email="user1@example.com",
    hashed_password="Hased_password",
    user_role=AccountRole.user,
    is_active=True,
    is_deleted=False
  )

@pytest.fixture()
def permit_payload(permit_account_obj):
  return {
    "sub": str(permit_account_obj.id),
    "role": permit_account_obj.user_role 
  }

@pytest.fixture()
def mock_permit_service():
  return AsyncMock()

@pytest.fixture()
async def unit_permit_client(mock_permit_service):
  app.dependency_overrides[get_permit_service] = lambda: mock_permit_service
  app.dependency_overrides[oauth2_scheme] = lambda: "jwt_token"

  async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
    yield c

  app.dependency_overrides.clear()

