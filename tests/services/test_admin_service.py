import pytest

import app.core.exceptions as e
from app.models.account_model import AccountRole

@pytest.mark.anyio
@pytest.mark.unit
async def test_view_all_accounts_success(mock_admin_db_repo, admin_service, mock_admin_account_list):
  mock_admin_db_repo.get_all_accounts.return_value = mock_admin_account_list

  result = await admin_service.view_all_accounts(0, 10)

  assert len(result) == 3
  assert result == mock_admin_account_list

@pytest.mark.anyio
@pytest.mark.unit
async def test_view_all_accounts_is_active_filter_success(mock_admin_db_repo, admin_service, mock_admin_account_list):
  mock_admin_db_repo.get_all_accounts.return_value = [mock_admin_account_list[1]]

  result = await admin_service.view_all_accounts(0, 10, False)

  assert len(result) == 1
  assert mock_admin_account_list[1] in result

@pytest.mark.anyio
@pytest.mark.unit
async def test_view_all_accounts_is_deketed_filter_success(mock_admin_db_repo, admin_service, mock_admin_account_list):
  mock_admin_db_repo.get_all_accounts.return_value = [mock_admin_account_list[2]]

  result = await admin_service.view_all_accounts(0, 10, None, True)

  assert len(result) == 1
  assert mock_admin_account_list[2] in result

@pytest.mark.anyio
@pytest.mark.unit
async def test_view_all_accounts_user_not_found_exception(mock_admin_db_repo, admin_service, mock_admin_account_list):
  mock_admin_db_repo.get_all_accounts.return_value = []

  with pytest.raises(e.UserNotFoundException) as exc:
    await admin_service.view_all_accounts(0, 10)

  assert exc.value.status_code == e.UserNotFoundException.status_code
  assert exc.value.detail == e.UserNotFoundException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_delete_account_success(mock_admin_db_repo, admin_service, mock_admin_account_list):
  account_obj = mock_admin_account_list[0]

  mock_admin_db_repo.get_by_id.return_value = account_obj

  account_obj.is_deleted = False

  mock_admin_db_repo.save.return_value = account_obj

  result = await admin_service.delete_account(1)

  assert result == account_obj

@pytest.mark.anyio
@pytest.mark.unit
async def test_delete_account_user_not_found_exception(mock_admin_db_repo, admin_service):
  mock_admin_db_repo.get_by_id.return_value = None

  with pytest.raises(e.UserNotFoundException) as exc:
    await admin_service.delete_account(14)

  assert exc.value.status_code == e.UserNotFoundException.status_code
  assert exc.value.detail == e.UserNotFoundException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_delete_account_already_deleted_exception(mock_admin_db_repo, admin_service, mock_admin_account_list):
  mock_admin_db_repo.get_by_id.return_value = mock_admin_account_list[2]

  with pytest.raises(e.AlreadyDeletedException) as exc:
    await admin_service.delete_account(3)

  assert exc.value.status_code == e.AlreadyDeletedException.status_code
  assert exc.value.detail == e.AlreadyDeletedException.detail