from unittest.mock import AsyncMock

import pytest

from app.models.account_model import Account
from app.repositories.account_repository import AccountDbRepository
from app.schemas.account_schema import AccountCreate
from app.services.account_service import AccountService
from tests.conftest import db_session

@pytest.fixture()
def db_repo(db_session):
  return AccountDbRepository(db_session)

@pytest.fixture()
def account_obj():
  return Account(
    username="user1",
    email="user1@example.com",
    hashed_password="HashedPassword123"
  )

@pytest.fixture()
async def saved_account_obj(db_repo, account_obj):
  return await db_repo.save(account_obj)

@pytest.fixture()
def mock_security():
  return AsyncMock()

@pytest.fixture()
def mock_db_repo():
  return AsyncMock()

@pytest.fixture()
def service(mock_security, mock_db_repo):
  return AccountService(mock_security, mock_db_repo)

@pytest.fixture()
def account_data():
  return AccountCreate(
    username="user1",
    email="user1@example.com",
    password="Password123"
  )