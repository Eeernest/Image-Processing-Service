from httpx import AsyncClient
import pytest

from app.core.exceptions import UsernameUnavailableException, EmailUnavailableException

@pytest.mark.anyio
@pytest.mark.unit
async def test_register_success(account_obj, mock_account_service, unit_account_client, account_payload):
  account_obj.id = 1
  
  mock_account_service.create_account.return_value = account_obj

  result = await unit_account_client.post("/register", json=account_payload)
  data = result.json()

  assert result.status_code == 200
  assert data["username"] == account_obj.username
  assert data["email"] == account_obj.email
  assert mock_account_service.create_account.call_count == 1

@pytest.mark.anyio
@pytest.mark.unit
async def test_register_username_excepion(mock_account_service, unit_account_client: AsyncClient, account_payload):
  mock_account_service.create_account.side_effect = UsernameUnavailableException()

  result = await unit_account_client.post("/register", json=account_payload)
  data = result.json()

  assert result.status_code == 409
  assert data["detail"] == UsernameUnavailableException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_register_email_exception(mock_account_service, unit_account_client: AsyncClient, account_payload):
  mock_account_service.create_account.side_effect = EmailUnavailableException

  result = await unit_account_client.post("/register", json=account_payload)
  data = result.json()

  assert result.status_code == 409
  assert data["detail"] == EmailUnavailableException.detail

@pytest.mark.anyio
@pytest.mark.integration
async def test_integration_register_success(account_obj, account_payload, integration_account_client: AsyncClient):
  result = await integration_account_client.post("/register", json=account_payload)
  data = result.json()

  assert result.status_code == 200
  assert data["id"] is not None
  assert data["username"] == account_obj.username
  assert data["email"] == account_obj.email