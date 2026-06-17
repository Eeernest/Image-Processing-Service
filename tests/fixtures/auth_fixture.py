from unittest.mock import AsyncMock

import pytest

from app.models.account_model import Account
from app.services.auth_service import AuthService

@pytest.fixture()
def mock_security():
  return AsyncMock()

@pytest.fixture()
def mock_db_repo():
  return AsyncMock()

@pytest.fixture()
def service(mock_security, mock_db_repo):
  return AuthService(mock_security, mock_db_repo)

@pytest.fixture()
def account_obj():
  return Account(
    username="user1",
    email="user1@example.com",
    hashed_password="Hashedpassword123"
  )