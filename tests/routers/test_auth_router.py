import pytest

from app.core.exceptions import InvalidCredentialsException
from tests.fixtures.auth_fixture import mock_service, unit_client, account_payload, token

@pytest.mark.anyio
@pytest.mark.unit
async def test_login_success(mock_service, unit_client, account_payload, token):
  mock_service.login.return_value = token

  result = await unit_client.post("/token", data=account_payload)
  data = result.json()

  assert result.status_code == 200
  assert data["access_token"] == token.access_token
  assert data["token_type"] == token.token_type

@pytest.mark.anyio
@pytest.mark.unit
async def test_login_data_failure(mock_service, unit_client, account_payload):
  mock_service.login.side_effect = InvalidCredentialsException()

  result = await unit_client.post("/token", data=account_payload)
  data = result.json()

  assert result.status_code == 401
  assert data["detail"] == InvalidCredentialsException.detail