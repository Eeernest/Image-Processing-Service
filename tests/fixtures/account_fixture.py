from unittest.mock import AsyncMock

from httpx import AsyncClient, ASGITransport
import pytest

from app.core.security import Security
from app.dependencies.account_dependency import get_account_service
from app.main import app
from app.models.account_model import Account
from app.repositories.account_db_repository import AccountDbRepository
from app.schemas.account_schema import AccountCreate
from app.services.account_service import AccountService

@pytest.fixture()
def account_db_repo(db_session):
  return AccountDbRepository(db_session)

@pytest.fixture()
def account_obj():
  return Account(
    username="user1",
    email="user1@example.com",
    hashed_password="HashedPassword123"
  )

@pytest.fixture()
async def saved_account_obj(account_db_repo, account_obj):
  return await account_db_repo.save(account_obj)

@pytest.fixture()
def mock_account_security():
  return AsyncMock()

@pytest.fixture()
def mock_account_db_repo():
  return AsyncMock()

@pytest.fixture()
def account_service(mock_account_security, mock_account_db_repo):
  return AccountService(mock_account_security, mock_account_db_repo)

@pytest.fixture()
def account_data():
  return AccountCreate(
    username="user1",
    email="user1@example.com",
    password="Password123"
  )

@pytest.fixture()
def mock_account_service():
  return AsyncMock()

@pytest.fixture()
async def unit_account_client(mock_account_service):
  app.dependency_overrides[get_account_service] = lambda: mock_account_service

  async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
    yield c

  app.dependency_overrides.clear()

@pytest.fixture()
def account_payload():
  return {
    "username": "user1",
    "email": "user1@example.com",
    "password": "Password123"
  }

@pytest.fixture()
def integration_account_service(db_session):
  security = Security()
  db_repo = AccountDbRepository(db_session)

  return AccountService(security, db_repo)

@pytest.fixture()
async def integration_account_client(integration_account_service):
  app.dependency_overrides[get_account_service] = lambda: integration_account_service

  async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
    yield c

  app.dependency_overrides.clear()