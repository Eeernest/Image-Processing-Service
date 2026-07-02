import pytest

from app.models.account_model import AccountRole

@pytest.mark.anyio
@pytest.mark.integration
async def test_save_succes(account_db_repo, account_obj):
  result = await account_db_repo.save(account_obj)

  assert result.id is not None
  assert result.username == account_obj.username
  assert result.email == account_obj.email
  assert result.user_role == AccountRole.user
  assert result.is_active == True
  assert result.is_deleted == False

@pytest.mark.anyio
@pytest.mark.integration
async def test_get_by_username_success(account_db_repo, saved_account_obj):
  result = await account_db_repo.get_by_username(saved_account_obj.username)

  assert result.username == saved_account_obj.username

@pytest.mark.anyio
@pytest.mark.integration
async def test_get_by_email_success(account_db_repo, saved_account_obj):
  result = await account_db_repo.get_by_email(saved_account_obj.email)

  assert result.email == saved_account_obj.email

@pytest.mark.anyio
@pytest.mark.integration
async def test_get_by_id(account_db_repo, saved_account_obj):
  result = await account_db_repo.get_by_id(saved_account_obj.id)

  assert result == saved_account_obj