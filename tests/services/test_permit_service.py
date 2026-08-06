import jwt
import pytest

import app.core.exceptions as e

@pytest.mark.anyio
@pytest.mark.unit
async def test_get_current_user_success(mock_permit_security, mock_permit_db_repo, permit_service, permit_account_obj, access_token_data):
  mock_permit_security.decode_jwt.return_value = access_token_data
  mock_permit_db_repo.get_by_id.return_value = permit_account_obj

  result = await permit_service.get_current_user("valid_access_token")

  assert result == permit_account_obj

@pytest.mark.anyio
@pytest.mark.unit
async def test_get_current_user_token_expired_exception(mock_permit_security, permit_service):
  mock_permit_security.decode_jwt.side_effect = jwt.ExpiredSignatureError()

  with pytest.raises(e.TokenExpiredException) as exc:
    await permit_service.get_current_user("expired_access_token")

  assert exc.value.status_code == e.TokenExpiredException.status_code
  assert exc.value.detail == e.TokenExpiredException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_get_current_user_py_jwt_error(mock_permit_security, permit_service):
  mock_permit_security.decode_jwt.side_effect = jwt.PyJWTError()

  with pytest.raises(e.InvalidTokenException) as exc:
    await permit_service.get_current_user("invalid_access_token")

  assert exc.value.status_code == e.InvalidTokenException.status_code
  assert exc.value.detail == e.InvalidTokenException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_get_current_user_sub_is_none_failure(mock_permit_security, permit_service, permit_account_obj):
  mock_permit_security.decode_jwt.return_value = {"sub": None, "role": permit_account_obj.user_role}

  with pytest.raises(e.InvalidTokenException) as exc:
      await permit_service.get_current_user("invalid_access_token")
  
  assert exc.value.status_code == e.InvalidTokenException.status_code
  assert exc.value.detail == e.InvalidTokenException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_get_current_user_role_is_none_failure(mock_permit_security, permit_service, permit_account_obj):
  mock_permit_security.decode_jwt.return_value = {"sub": permit_account_obj.id, "role": None}
  
  with pytest.raises(e.InvalidTokenException) as exc:
      await permit_service.get_current_user("invalid_access_token")
  
  assert exc.value.status_code == e.InvalidTokenException.status_code
  assert exc.value.detail == e.InvalidTokenException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_get_current_user_account_is_none_failure(mock_permit_security, mock_permit_db_repo, permit_service, access_token_data):
  mock_permit_security.decode_jwt.return_value = access_token_data
  mock_permit_db_repo.get_by_id.return_value = None

  with pytest.raises(e.InvalidTokenException) as exc:
    await permit_service.get_current_user("invalid_access_token")
  
  assert exc.value.status_code == e.InvalidTokenException.status_code
  assert exc.value.detail == e.InvalidTokenException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_get_current_user_account_is_inactive_failure(mock_permit_security, mock_permit_db_repo, permit_service, permit_account_obj, access_token_data):
  permit_account_obj.is_active = False

  mock_permit_security.decode_jwt.return_value = access_token_data
  mock_permit_db_repo.get_by_id.return_value = permit_account_obj

  with pytest.raises(e.InactiveAccountException) as exc:
    await permit_service.get_current_user("invalid_access_token")
  
  assert exc.value.status_code == e.InactiveAccountException.status_code
  assert exc.value.detail == e.InactiveAccountException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_get_current_user_account_is_inactive_failure(mock_permit_security, mock_permit_db_repo, permit_service, permit_account_obj, access_token_data):
  permit_account_obj.is_deleted = True

  mock_permit_security.decode_jwt.return_value = access_token_data
  mock_permit_db_repo.get_by_id.return_value = permit_account_obj

  with pytest.raises(e.DeletedAccountException) as exc:
    await permit_service.get_current_user("invalid_access_token")
  
  assert exc.value.status_code == e.DeletedAccountException.status_code
  assert exc.value.detail == e.DeletedAccountException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_get_current_admin_success(mock_permit_security, mock_permit_db_repo, permit_service, permit_admin_obj, admin_access_token_data):
  mock_permit_security.decode_jwt.return_value = admin_access_token_data
  mock_permit_db_repo.get_by_id.return_value = permit_admin_obj

  result = await permit_service.get_current_admin("valid_access_token")

  assert result == permit_admin_obj

@pytest.mark.anyio
@pytest.mark.unit
async def test_get_current_admin_token_expired_exception(mock_permit_security, permit_service):
  mock_permit_security.decode_jwt.side_effect = jwt.ExpiredSignatureError()

  with pytest.raises(e.TokenExpiredException) as exc:
    await permit_service.get_current_admin("expired_access_token")

  assert exc.value.status_code == e.TokenExpiredException.status_code
  assert exc.value.detail == e.TokenExpiredException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_get_current_admin_py_jwt_error(mock_permit_security, permit_service):
  mock_permit_security.decode_jwt.side_effect = jwt.PyJWTError()

  with pytest.raises(e.InvalidTokenException) as exc:
    await permit_service.get_current_admin("invalid_access_token")

  assert exc.value.status_code == e.InvalidTokenException.status_code
  assert exc.value.detail == e.InvalidTokenException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_get_current_admin_sub_is_none_failure(mock_permit_security, permit_service, permit_admin_obj):
  mock_permit_security.decode_jwt.return_value = {"sub": None, "role": permit_admin_obj.user_role}

  with pytest.raises(e.InvalidTokenException) as exc:
      await permit_service.get_current_admin("invalid_access_token")
  
  assert exc.value.status_code == e.InvalidTokenException.status_code
  assert exc.value.detail == e.InvalidTokenException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_get_current_admin_role_is_none_failure(mock_permit_security, permit_service, permit_admin_obj):
  mock_permit_security.decode_jwt.return_value = {"sub": permit_admin_obj.id, "role": None}
  
  with pytest.raises(e.InvalidTokenException) as exc:
      await permit_service.get_current_admin("invalid_access_token")
  
  assert exc.value.status_code == e.InvalidTokenException.status_code
  assert exc.value.detail == e.InvalidTokenException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_get_current_admin_role_is_user_failure(mock_permit_security, permit_service, access_token_data):
  mock_permit_security.decode_jwt.return_value = access_token_data
  
  with pytest.raises(e.InvalidTokenException) as exc:
      await permit_service.get_current_admin("invalid_access_token")
  
  assert exc.value.status_code == e.InvalidTokenException.status_code
  assert exc.value.detail == e.InvalidTokenException.detail


@pytest.mark.anyio
@pytest.mark.unit
async def test_get_current_admin_account_is_none_failure(mock_permit_security, mock_permit_db_repo, permit_service, admin_access_token_data):
  mock_permit_security.decode_jwt.return_value = admin_access_token_data
  mock_permit_db_repo.get_by_id.return_value = None

  with pytest.raises(e.InvalidTokenException) as exc:
    await permit_service.get_current_admin("invalid_access_token")
  
  assert exc.value.status_code == e.InvalidTokenException.status_code
  assert exc.value.detail == e.InvalidTokenException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_get_current_admin_account_is_inactive_failure(mock_permit_security, mock_permit_db_repo, permit_service, permit_admin_obj, admin_access_token_data):
  permit_admin_obj.is_active = False

  mock_permit_security.decode_jwt.return_value = admin_access_token_data
  mock_permit_db_repo.get_by_id.return_value = permit_admin_obj

  with pytest.raises(e.InactiveAccountException) as exc:
    await permit_service.get_current_admin("invalid_access_token")
  
  assert exc.value.status_code == e.InactiveAccountException.status_code
  assert exc.value.detail == e.InactiveAccountException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_get_current_admin_account_is_inactive_failure(mock_permit_security, mock_permit_db_repo, permit_service, permit_admin_obj, admin_access_token_data):
  permit_admin_obj.is_deleted = True

  mock_permit_security.decode_jwt.return_value = admin_access_token_data
  mock_permit_db_repo.get_by_id.return_value = permit_admin_obj

  with pytest.raises(e.DeletedAccountException) as exc:
    await permit_service.get_current_admin("invalid_access_token")
  
  assert exc.value.status_code == e.DeletedAccountException.status_code
  assert exc.value.detail == e.DeletedAccountException.detail