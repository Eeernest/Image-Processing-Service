import pytest

from app.core.exceptions import InvalidCredentialsException

@pytest.mark.anyio
@pytest.mark.unit
async def test_login_success(mock_auth_service, unit_auth_client, auth_account_payload, token):
  mock_auth_service.login.return_value = token

  result = await unit_auth_client.post("/token", data=auth_account_payload)
  data = result.json()

  assert result.status_code == 200
  assert data["access_token"] == token.access_token
  assert data["token_type"] == token.token_type

@pytest.mark.anyio
@pytest.mark.unit
async def test_login_data_failure(mock_auth_service, unit_auth_client, auth_account_payload):
  mock_auth_service.login.side_effect = InvalidCredentialsException()

  result = await unit_auth_client.post("/token", data=auth_account_payload)
  data = result.json()

  assert result.status_code == 401
  assert data["detail"] == InvalidCredentialsException.detail