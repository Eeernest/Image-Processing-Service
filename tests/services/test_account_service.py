import pytest
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import UsernameUnavailableException, EmailUnavailableException

@pytest.mark.anyio
@pytest.mark.unit
async def test_create_account_success(account_obj, mock_account_security, mock_account_db_repo, account_service, account_data):
  mock_account_db_repo.get_by_username.return_value = None
  mock_account_db_repo.get_by_email.return_value = None
  mock_account_security.get_password_hash.return_value = account_obj.hashed_password
  mock_account_db_repo.save.return_value = account_obj


  result = await account_service.create_account(account_data)

  assert result.username == account_data.username
  assert result.email == account_data.email
  assert mock_account_db_repo.save.call_count == 1

@pytest.mark.anyio
@pytest.mark.unit
async def test_create_account_username_exception(account_obj, mock_account_db_repo, account_service, account_data):
  mock_account_db_repo.get_by_username.return_value = account_obj

  with pytest.raises(UsernameUnavailableException) as exc:
    await account_service.create_account(account_data)

  assert exc.value.status_code == 409
  assert f"Username '{account_data.username}' is already in use" in str(exc.value)

@pytest.mark.anyio
@pytest.mark.unit
async def test_create_account_email_exception(account_obj, mock_account_db_repo, account_service, account_data):
  mock_account_db_repo.get_by_username.return_value = None
  mock_account_db_repo.get_by_email.return_value = account_obj

  with pytest.raises(EmailUnavailableException) as exc:
    await account_service.create_account(account_data)

  assert exc.value.status_code == 409
  assert f"Email '{account_data.email}' is already in use" in str(exc.value)

@pytest.mark.anyio
@pytest.mark.unit
async def test_create_account_username_race_condition(account_obj, mock_account_security, mock_account_db_repo, account_service, account_data):
  mock_account_db_repo.get_by_username.return_value = None
  mock_account_db_repo.get_by_email.return_value = None
  mock_account_security.get_password_hash.return_value = account_obj.hashed_password
  mock_account_db_repo.save.side_effect = IntegrityError("stmt", "params", "username")

  with pytest.raises(UsernameUnavailableException) as exc:
    await account_service.create_account(account_data)

  assert exc.value.status_code == 409
  assert f"Username '{account_data.username}' is already in use" in str(exc.value)

@pytest.mark.anyio
@pytest.mark.unit
async def test_create_account_email_race_condition(account_obj, mock_account_security, mock_account_db_repo, account_service, account_data):
  mock_account_db_repo.get_by_username.return_value = None
  mock_account_db_repo.get_ny_email.return_value = None
  mock_account_security.get_password_hash.return_value = account_obj.hashed_password
  mock_account_db_repo.save.side_effect = IntegrityError("stmt", "params", "email")

  with pytest.raises(EmailUnavailableException) as exc:
    await account_service.create_account(account_data)

  assert exc.value.status_code == 409
  assert f"Email '{account_data.email}' is already in use" in str(exc.value)