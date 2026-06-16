import pytest

from app.core.exceptions import UsernameUnavailableException, EmailUnavailableException, PasswordTooShortException
from tests.fixtures.account_fixture import account_obj, mock_service, unit_client, account_payload, integration_service, integration_client

@pytest.mark.anyio
@pytest.mark.unit
async def test_register_success(account_obj, mock_service, unit_client, account_payload):
  account_obj.id = 1
  
  mock_service.create_account.return_value = account_obj

  result = await unit_client.post("/register", json=account_payload)
  data = result.json()

  assert result.status_code == 200
  assert data["username"] == account_obj.username
  assert data["email"] == account_obj.email
  assert mock_service.create_account.call_count == 1

@pytest.mark.anyio
@pytest.mark.unit
async def test_register_username_excepion(mock_service, unit_client, account_payload):
  mock_service.create_account.side_effect = UsernameUnavailableException()

  result = await unit_client.post("/register", json=account_payload)
  data = result.json()

  assert result.status_code == 409
  assert data["detail"] == UsernameUnavailableException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_register_email_exception(mock_service, unit_client, account_payload):
  mock_service.create_account.side_effect = EmailUnavailableException

  result = await unit_client.post("/register", json=account_payload)
  data = result.json()

  assert result.status_code == 409
  assert data["detail"] == EmailUnavailableException.detail

@pytest.mark.anyio
@pytest.mark.integration
async def test_integration_register_success(account_obj, account_payload, integration_client):
  result = await integration_client.post("/register", json=account_payload)
  data = result.json()

  assert result.status_code == 200
  assert data["id"] is not None
  assert data["username"] == account_obj.username
  assert data["email"] == account_obj.email