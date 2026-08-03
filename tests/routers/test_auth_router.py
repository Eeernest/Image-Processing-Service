import pytest

import app.core.exceptions as e

@pytest.mark.anyio
@pytest.mark.unit
async def test_login_success(mock_auth_service, unit_auth_client, auth_account_payload, mock_tokens):
  mock_auth_service.login.return_value = mock_tokens

  result = await unit_auth_client.post("/token", data={"username": "user1", "password": "Password123"})
  data = result.json()

  assert result.status_code == 200
  assert data["access_token"] == mock_tokens.access_token
  assert data["refresh_token"] == mock_tokens.refresh_token
  assert data["token_type"] == mock_tokens.token_type

@pytest.mark.anyio
@pytest.mark.unit
async def test_login_data_failure(mock_auth_service, unit_auth_client, auth_account_payload):
  mock_auth_service.login.side_effect = e.InvalidCredentialsException()

  result = await unit_auth_client.post("/token", data={"username": "user1", "password": "wrongpassword"})
  data = result.json()

  assert result.status_code == 401
  assert data["detail"] == e.InvalidCredentialsException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_refresh_token_success(mock_auth_service, unit_auth_client, mock_tokens):
  mock_auth_service.refresh_token.return_value = mock_tokens

  result = await unit_auth_client.post("/refresh_token", json={"refresh_token": "curent_refresh_token"})
  data = result.json()

  assert result.status_code == 200
  assert data["access_token"] == mock_tokens.access_token
  assert data["refresh_token"] == mock_tokens.refresh_token
  assert data["token_type"] == mock_tokens.token_type

@pytest.mark.anyio
@pytest.mark.unit
async def test_refresh_token_expired_exception(mock_auth_service, unit_auth_client):
  mock_auth_service.refresh_token.side_effect = e.TokenExpiredException()

  result = await unit_auth_client.post("/refresh_token", json={"refresh_token": "expired_refresh_token"})
  data = result.json()

  assert result.status_code == 401
  assert data["detail"] == e.TokenExpiredException.detail