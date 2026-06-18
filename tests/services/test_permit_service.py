from jwt.exceptions import InvalidTokenError
import pytest

from app.core.exceptions import InvalidTokenException, InactiveAccountException, DeletedAccountException
from tests.fixtures.permit_fixture import mock_security, mock_db_repo, service, account_obj, payload

@pytest.mark.anyio
@pytest.mark.unit
async def test_get_current_user_success(mock_security, mock_db_repo, service, account_obj, payload):
  mock_security.decode_jwt.return_value = payload
  mock_db_repo.get_by_id.return_value = account_obj

  result = await service.get_current_user("valid_token")

  assert result.username == account_obj.username

@pytest.mark.anyio
@pytest.mark.unit
async def test_get_current_user_invalid_token_error(mock_security, service):
  mock_security.decode_jwt.side_effect = InvalidTokenError

  with pytest.raises(InvalidTokenException) as exc:
    await service.get_current_user("exc_token")

  assert exc.value.status_code == 401
  assert exc.value.detail == InvalidTokenException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_get_current_user_no_account_id_failure(mock_security, service, payload):
  payload["sub"] = None

  mock_security.decode_jwt.return_value = payload

  with pytest.raises(InvalidTokenException) as exc:
    await service.get_current_user("exc_token")

  assert exc.value.status_code == 401
  assert exc.value.detail == InvalidTokenException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_get_current_user_no_account_failure(mock_security, mock_db_repo, service, payload):
  mock_security.decode_jwt.return_value = payload
  mock_db_repo.get_by_id.return_value = None

  with pytest.raises(InvalidTokenException) as exc:
    await service.get_current_user("exc_token")

  assert exc.value.status_code == 401
  assert exc.value.detail == InvalidTokenException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_get_current_user_inactive_account_exception(mock_security, mock_db_repo, service, account_obj, payload):
  account_obj.is_active = False

  mock_security.decode_jwt.return_value = payload
  mock_db_repo.get_by_id.return_value = account_obj

  with pytest.raises(InactiveAccountException) as exc:
    await service.get_current_user("exc_token")

  assert exc.value.status_code == 400
  assert exc.value.detail == InactiveAccountException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_get_current_user_deleted_account_exception(mock_security, mock_db_repo, service, account_obj, payload):
  account_obj.is_deleted = True

  mock_security.decode_jwt.return_value = payload
  mock_db_repo.get_by_id.return_value = account_obj

  with pytest.raises(DeletedAccountException) as exc:
    await service.get_current_user("exc_token")

  assert exc.value.status_code == 400
  assert exc.value.detail == DeletedAccountException.detail