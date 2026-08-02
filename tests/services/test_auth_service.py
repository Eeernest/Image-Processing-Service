import jwt
import pytest
from redis.exceptions import RedisError

import app.core.exceptions as e

@pytest.mark.anyio
@pytest.mark.unit
async def test_login_success(mock_auth_security, mock_auth_db_repo, mock_auth_redis_repo, auth_service, auth_account_obj):
  mock_auth_db_repo.get_by_username.return_value = auth_account_obj
  mock_auth_security.verify_password.return_value = True
  mock_auth_security.create_access_token.return_value = "fake_access_token"
  mock_auth_security.create_refresh_token.return_value = "fake_refresh_token"
  mock_auth_redis_repo.store_refresh_token.return_value = None

  result = await auth_service.login(auth_account_obj.username, "Password123")

  assert result.access_token == "fake_access_token"
  assert result.refresh_token == "fake_refresh_token"
  assert result.token_type == "bearer"

@pytest.mark.anyio
@pytest.mark.unit
async def test_login_username_failure(mock_auth_security, mock_auth_db_repo, auth_service):
  mock_auth_db_repo.get_by_username.return_value = None
  mock_auth_security.verify_password.return_value = False

  with pytest.raises(e.InvalidCredentialsException) as exc:
    await auth_service.login("random_user", "Password123")

  assert exc.value.status_code == 401
  assert exc.value.detail == e.InvalidCredentialsException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_login_password_failure(mock_auth_security, mock_auth_db_repo, auth_service, auth_account_obj):
  mock_auth_db_repo.get_by_username.return_value = auth_account_obj
  mock_auth_security.verify_password.return_value = False

  with pytest.raises(e.InvalidCredentialsException) as exc:
    await auth_service.login(auth_account_obj.username, "Wrongpassword123")

  assert exc.value.status_code == 401
  assert exc.value.detail == e.InvalidCredentialsException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_login_redis_failure_exception(mock_auth_security, mock_auth_db_repo, mock_auth_redis_repo, auth_service, auth_account_obj):
  mock_auth_db_repo.get_by_username.return_value = auth_account_obj
  mock_auth_security.verify_password.return_value = True
  mock_auth_security.create_access_token.return_value = "fake_access_token"
  mock_auth_security.create_refresh_token.return_value = "fake_refresh_token"
  mock_auth_redis_repo.store_refresh_token.side_effect = RedisError

  with pytest.raises(e.RedisFailureException) as exc:
    await auth_service.login(auth_account_obj.username, "Password123")

  assert exc.value.status_code == e.RedisFailureException.status_code
  assert exc.value.detail == e.RedisFailureException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_refresh_token_success(mock_auth_security, mock_auth_db_repo, mock_auth_redis_repo, auth_service, auth_account_obj, mock_refresh_token_data):
  mock_auth_security.decode_jwt.return_value = mock_refresh_token_data
  mock_auth_redis_repo.delete_refresh_token.return_value = None
  mock_auth_db_repo.get_by_id.return_value = auth_account_obj
  mock_auth_security.create_access_token.return_value = "fake_access_token"
  mock_auth_security.create_refresh_token.return_value = "fake_refresh_token"
  mock_auth_redis_repo.store_refresh_token.return_value = None

  result = await auth_service.refresh_token("fake_refresh_token")

  assert result.access_token == "fake_access_token"
  assert result.refresh_token == "fake_refresh_token"
  assert result.token_type == "bearer"

@pytest.mark.anyio
@pytest.mark.unit
async def test_refresh_token_expired_exception(mock_auth_security, auth_service):
  mock_auth_security.decode_jwt.side_effect = jwt.ExpiredSignatureError()

  with pytest.raises(e.TokenExpiredException) as exc:
    await auth_service.refresh_token("fake_refresh_token")

  assert exc.value.status_code == e.TokenExpiredException.status_code
  assert exc.value.detail == e.TokenExpiredException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_refresh_token_decode_invalid_exception(mock_auth_security, auth_service):
  mock_auth_security.decode_jwt.side_effect = jwt.PyJWTError()

  with pytest.raises(e.InvalidTokenException) as exc:
    await auth_service.refresh_token("fake_refresh_token")

  assert exc.value.status_code == e.InvalidTokenException.status_code
  assert exc.value.detail == e.InvalidTokenException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_refresh_token_delete_failure(mock_auth_security, mock_auth_redis_repo, auth_service, mock_refresh_token_data):
  mock_auth_security.decode_jwt.return_value = mock_refresh_token_data
  mock_auth_redis_repo.delete_refresh_token.side_effect = RedisError()

  with pytest.raises(e.RedisFailureException) as exc:
    await auth_service.refresh_token("fake_refresh_token")

  assert exc.value.status_code == e.RedisFailureException.status_code
  assert exc.value.detail == e.RedisFailureException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_refresh_token_get_by_id_failure(mock_auth_security, mock_auth_db_repo, mock_auth_redis_repo, auth_service, mock_refresh_token_data):
  mock_auth_security.decode_jwt.return_value = mock_refresh_token_data
  mock_auth_redis_repo.delete_refresh_token.return_value = None
  mock_auth_db_repo.get_by_id.return_value = None

  with pytest.raises(e.InvalidTokenException) as exc:
    await auth_service.refresh_token("fake_refresh_token")

  assert exc.value.status_code == e.InvalidTokenException.status_code
  assert exc.value.detail == e.InvalidTokenException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_refresh_token_store_failure(mock_auth_security, mock_auth_db_repo, mock_auth_redis_repo, auth_service, auth_account_obj, mock_refresh_token_data):
  mock_auth_security.decode_jwt.return_value = mock_refresh_token_data
  mock_auth_redis_repo.delete_refresh_token.return_value = None
  mock_auth_db_repo.get_by_id.return_value = auth_account_obj
  mock_auth_redis_repo.store_refresh_token.side_effect = RedisError()

  with pytest.raises(e.RedisFailureException) as exc:
    await auth_service.refresh_token("fake_refresh_token")

  assert exc.value.status_code == e.RedisFailureException.status_code
  assert exc.value.detail == e.RedisFailureException.detail