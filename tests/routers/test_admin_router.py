import pytest

import app.core.exceptions as e

@pytest.mark.anyio
@pytest.mark.unit
async def test_view_all_accounts_succses(mock_admin_account_list, mock_admin_service, unit_admin_client):
  mock_admin_service.view_all_accounts.return_value = mock_admin_account_list

  result = await unit_admin_client.get("/view_all_accounts", params={"offset": 0, "limit": 100})
  data = result.json()

  assert result.status_code == 200
  assert len(data) == 3

@pytest.mark.anyio
@pytest.mark.unit
async def test_view_all_accounts_user_not_fount_exception(mock_admin_service, unit_admin_client):
  mock_admin_service.view_all_accounts.side_effect = e.UserNotFoundException()

  result = await unit_admin_client.get("/view_all_accounts", params={"offset": 10, "limit": 100})
  data = result.json()

  assert result.status_code == 404
  assert data["detail"] == e.UserNotFoundException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_delete_account_success(mock_admin_account_list, mock_admin_service, unit_admin_client):
  mock_admin_account_list[0].is_deleted = True

  mock_admin_service.delete_account.return_value = mock_admin_account_list[0]

  result = await unit_admin_client.patch("/delete_account", params={"id": mock_admin_account_list[0].id})

  assert result.status_code == 200