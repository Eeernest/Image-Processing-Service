import pytest

import app.core.exceptions as e
from app.models.account_model import AccountRole

@pytest.mark.anyio
@pytest.mark.unit
async def test_view_all_accounts_success(mock_admin_db_repo, admin_service, mock_admin_account_list):
  mock_admin_db_repo.get_all_accounts.return_value = mock_admin_account_list

  result = await admin_service.view_all_accounts()

  assert len(result) == 3
  assert result == mock_admin_account_list

@pytest.mark.anyio
@pytest.mark.unit
async def test_view_all_accounts_is_active_filter_success(mock_admin_db_repo, admin_service, mock_admin_account_list):
  mock_admin_db_repo.get_all_accounts.return_value = [mock_admin_account_list[1]]

  result = await admin_service.view_all_accounts(False)

  assert len(result) == 1
  assert mock_admin_account_list[1] in result

@pytest.mark.anyio
@pytest.mark.unit
async def test_view_all_accounts_is_deketed_filter_success(mock_admin_db_repo, admin_service, mock_admin_account_list):
  mock_admin_db_repo.get_all_accounts.return_value = [mock_admin_account_list[2]]

  result = await admin_service.view_all_accounts(None, True)

  assert len(result) == 1
  assert mock_admin_account_list[2] in result

@pytest.mark.anyio
@pytest.mark.unit
async def test_view_all_accounts_user_not_found_exception(mock_admin_db_repo, admin_service):
  mock_admin_db_repo.get_all_accounts.return_value = []

  with pytest.raises(e.UserNotFoundException) as exc:
    await admin_service.view_all_accounts()

  assert exc.value.status_code == e.UserNotFoundException.status_code
  assert exc.value.detail == e.UserNotFoundException.detail