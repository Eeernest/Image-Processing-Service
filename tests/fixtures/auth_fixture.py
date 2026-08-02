from unittest.mock import AsyncMock, Mock

from httpx import AsyncClient, ASGITransport
import pytest

from app.dependencies.auth_dependency import get_auth_service
from app.main import app
from app.models.account_model import Account
from app.schemas.token_schema import TokenBase
from app.services.auth_service import AuthService

@pytest.fixture()
def mock_auth_security():
  mock = AsyncMock()
  mock.create_access_token = Mock()
  mock.create_refresh_token = Mock()
  mock.encode_jwt = Mock()

  return mock

@pytest.fixture()
def mock_auth_db_repo():
  return AsyncMock()

@pytest.fixture()
def auth_service(mock_auth_security, mock_auth_db_repo):
  return AuthService(mock_auth_security, mock_auth_db_repo)

@pytest.fixture()
def auth_account_obj():
  return Account(
    username="user1",
    email="user1@example.com",
    hashed_password="Hashedpassword123"
  )

@pytest.fixture()
def mock_auth_service():
  return AsyncMock()

@pytest.fixture()
async def unit_auth_client(mock_auth_service):
  app.dependency_overrides[get_auth_service] = lambda: mock_auth_service

  async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
    yield c

  app.dependency_overrides.clear()

@pytest.fixture()
def auth_account_payload():
  return {
    "username": "user1",
    "password": "Password123"
  }

@pytest.fixture()
def token():
  return TokenBase(
    access_token="fake_access_token",
    refresh_token="fake_refresh_token",
    token_type="bearer"
  )