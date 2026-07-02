from jwt.exceptions import InvalidTokenError
import pytest

from app.core.exceptions import InvalidTokenException, InactiveAccountException, DeletedAccountException

@pytest.mark.anyio
@pytest.mark.unit
async def test_get_current_user_success(mock_permit_security, mock_permit_db_repo, permit_service, permit_account_obj, permit_payload):
  mock_permit_security.decode_jwt.return_value = permit_payload
  mock_permit_db_repo.get_by_id.return_value = permit_account_obj

  result = await permit_service.get_current_user("valid_token")

  assert result.username == permit_account_obj.username

@pytest.mark.anyio
@pytest.mark.unit
async def test_get_current_user_invalid_token_error(mock_permit_security, permit_service):
  mock_permit_security.decode_jwt.side_effect = InvalidTokenError

  with pytest.raises(InvalidTokenException) as exc:
    await permit_service.get_current_user("exc_token")

  assert exc.value.status_code == 401
  assert exc.value.detail == InvalidTokenException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_get_current_user_no_account_id_failure(mock_permit_security, permit_service, permit_payload):
  permit_payload["sub"] = None

  mock_permit_security.decode_jwt.return_value = permit_payload

  with pytest.raises(InvalidTokenException) as exc:
    await permit_service.get_current_user("exc_token")

  assert exc.value.status_code == 401
  assert exc.value.detail == InvalidTokenException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_get_current_user_no_account_failure(mock_permit_security, mock_permit_db_repo, permit_service, permit_payload):
  mock_permit_security.decode_jwt.return_value = permit_payload
  mock_permit_db_repo.get_by_id.return_value = None

  with pytest.raises(InvalidTokenException) as exc:
    await permit_service.get_current_user("exc_token")

  assert exc.value.status_code == 401
  assert exc.value.detail == InvalidTokenException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_get_current_user_inactive_account_exception(mock_permit_security, mock_permit_db_repo, permit_service, permit_account_obj, permit_payload):
  permit_account_obj.is_active = False

  mock_permit_security.decode_jwt.return_value = permit_payload
  mock_permit_db_repo.get_by_id.return_value = permit_account_obj

  with pytest.raises(InactiveAccountException) as exc:
    await permit_service.get_current_user("exc_token")

  assert exc.value.status_code == 400
  assert exc.value.detail == InactiveAccountException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_get_current_user_deleted_account_exception(mock_permit_security, mock_permit_db_repo, permit_service, permit_account_obj, permit_payload):
  permit_account_obj.is_deleted = True

  mock_permit_security.decode_jwt.return_value = permit_payload
  mock_permit_db_repo.get_by_id.return_value = permit_account_obj

  with pytest.raises(DeletedAccountException) as exc:
    await permit_service.get_current_user("exc_token")

  assert exc.value.status_code == 400
  assert exc.value.detail == DeletedAccountException.detail