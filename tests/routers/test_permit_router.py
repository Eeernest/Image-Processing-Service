import pytest

from app.core.exceptions import InvalidTokenException, InactiveAccountException, DeletedAccountException

@pytest.mark.anyio
@pytest.mark.unit
async def test_read_user_me_success(permit_account_obj, mock_permit_service, unit_permit_client):
  mock_permit_service.get_current_user.return_value = permit_account_obj

  result = await unit_permit_client.get("/users/me")
  data = result.json()
  
  assert result.status_code == 200
  assert data["username"] == permit_account_obj.username
  assert data["email"] == permit_account_obj.email

@pytest.mark.anyio
@pytest.mark.unit
async def test_read_user_me_invalid_token_exception(mock_permit_service, unit_permit_client):
  mock_permit_service.get_current_user.side_effect = InvalidTokenException()

  result = await unit_permit_client.get("/users/me")
  data = result.json()

  assert result.status_code == 401
  assert data["detail"] == InvalidTokenException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_read_user_me_inactive_user_exception(mock_permit_service, unit_permit_client):
  mock_permit_service.get_current_user.side_effect = InactiveAccountException()

  result = await unit_permit_client.get("/users/me")
  data = result.json()

  assert result.status_code == 400
  assert data["detail"] == InactiveAccountException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_read_user_me_deleted_account_excepion(mock_permit_service, unit_permit_client):
  mock_permit_service.get_current_user.side_effect = DeletedAccountException()

  result = await unit_permit_client.get("/users/me")
  data = result.json()

  assert result.status_code == 400
  assert data["detail"] == DeletedAccountException.detail