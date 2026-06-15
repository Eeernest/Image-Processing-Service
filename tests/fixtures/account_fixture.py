import pytest

from app.models.account_model import Account
from app.repositories.account_repository import AccountDbRepository
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