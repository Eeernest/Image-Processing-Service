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
async def test_delete_account_success(mock_admin_db_repo, admin_service, mock_admin_account_list):
  mock_admin_db_repo.get_by_id.return_value = mock_admin_account_list[0]

  mock_admin_db_repo.save.return_value = mock_admin_account_list[0]

  result = await admin_service.delete_account(mock_admin_account_list[0].id)

  assert result.is_deleted == True

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

@pytest.mark.anyio
@pytest.mark.unit
async def test_delete_account_failed_to_save_exception(mock_admin_account_list, mock_admin_db_repo, admin_service):
  mock_admin_db_repo.get_by_id.return_value = mock_admin_account_list[0]
  mock_admin_db_repo.save.side_effect = e.FailedToSaveException()

  with pytest.raises(e.FailedToSaveException) as exc:
    await admin_service.delete_account(mock_admin_account_list[0].id)

  assert exc.value.status_code == e.FailedToSaveException.status_code
  assert exc.value.detail == e.FailedToSaveException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_change_account_role_success(mock_admin_db_repo, admin_service, mock_admin_account_list):
  mock_admin_db_repo.get_by_id.return_value = mock_admin_account_list[0]

  mock_admin_db_repo.save.return_value = mock_admin_account_list[0]

  result = await admin_service.change_account_role(mock_admin_account_list[0].id, AccountRole.admin)

  assert result.user_role == AccountRole.admin

@pytest.mark.anyio
@pytest.mark.unit
async def test_change_account_role_user_not_found_exception(mock_admin_db_repo, admin_service):
  mock_admin_db_repo.get_by_id.return_value = None

  with pytest.raises(e.UserNotFoundException) as exc:
    await admin_service.change_account_role(1, AccountRole.admin)

  assert exc.value.status_code == e.UserNotFoundException.status_code
  assert exc.value.detail == e.UserNotFoundException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_change_account_role_already_changed_exception(mock_admin_account_list, mock_admin_db_repo, admin_service):
  mock_admin_db_repo.get_by_id.return_value = mock_admin_account_list[0]

  with pytest.raises(e.RoleAlreadyChangedException) as exc:
    await admin_service.change_account_role(mock_admin_account_list[0].id, AccountRole.user)

  assert exc.value.status_code == e.RoleAlreadyChangedException.status_code
  assert exc.value.detail == e.RoleAlreadyChangedException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_change_account_role_failed_to_save_exception(mock_admin_account_list, mock_admin_db_repo, admin_service):
  mock_admin_db_repo.get_by_id.return_value = mock_admin_account_list[0]
  mock_admin_db_repo.save.side_effect = e.FailedToSaveException()

  with pytest.raises(e.FailedToSaveException) as exc:
    await admin_service.change_account_role(mock_admin_account_list[0].id, AccountRole.admin)

  assert exc.value.status_code == e.FailedToSaveException.status_code
  assert exc.value.detail == e.FailedToSaveException.detail