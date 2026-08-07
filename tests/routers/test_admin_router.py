import pytest

@pytest.mark.anyio
@pytest.mark.unit
async def test_view_all_accounts_succses(mock_admin_account_list, mock_admin_service, unit_admin_client):
  mock_admin_service.view_all_accounts.return_value = mock_admin_account_list

  result = await unit_admin_client.get("/view_all_accounts", params={"offset": 0, "limit": 100})

  assert result.status_code == 200