from unittest.mock import AsyncMock, Mock

import pytest

from app.models.account_model import AccountRole, Account
from app.schemas.token_schema import TokenData
from app.services.permit_service import PermitService

@pytest.fixture()
def mock_security():
  mock = AsyncMock()
  mock.decode_jwt = Mock()

  return mock

@pytest.fixture()
def mock_db_repo():
  return AsyncMock()

@pytest.fixture()
def service(mock_security, mock_db_repo):
  return PermitService(mock_security, mock_db_repo)

@pytest.fixture()
def account_obj():
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
def payload(account_obj):
  return {
    "sub": str(account_obj.id),
    "role": account_obj.user_role 
  }