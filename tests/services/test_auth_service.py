import pytest

from app.core.exceptions import InvalidCredentialsException

@pytest.mark.anyio
@pytest.mark.unit
async def test_login_success(mock_auth_security, mock_account_db_repo, auth_service, auth_account_obj):
  mock_account_db_repo.get_by_username.return_value = auth_account_obj
  mock_auth_security.verify_password.return_value = True
  mock_auth_security.encode_jwt.return_value = "jwt_token"

  result = await auth_service.login(auth_account_obj.username, "Password123")

  assert result.access_token == "jwt_token"
  assert result.token_type == "bearer"

@pytest.mark.anyio
@pytest.mark.unit
async def test_login_username_failure(mock_auth_security, mock_account_db_repo, auth_service):
  mock_account_db_repo.get_by_username.return_value = None
  mock_auth_security.verify_password.return_value = False

  with pytest.raises(InvalidCredentialsException) as exc:
    await auth_service.login("random_user", "Password123")

  assert exc.value.status_code == 401
  assert exc.value.detail == InvalidCredentialsException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_login_password_failure(mock_auth_security, mock_account_db_repo, auth_service, auth_account_obj):
  mock_account_db_repo.get_by_username.return_value = auth_account_obj
  mock_auth_security.verify_password.return_value = False

  with pytest.raises(InvalidCredentialsException) as exc:
    await auth_service.login(auth_account_obj.username, "Wrongpassword123")

  assert exc.value.status_code == 401
  assert exc.value.detail == InvalidCredentialsException.detail