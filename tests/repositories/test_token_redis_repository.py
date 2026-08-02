import pytest

@pytest.mark.anyio
@pytest.mark.integration
async def test_store_refresh_token_and_get_account_id_success(token_redis_repo, refresh_token_data):
  await token_redis_repo.store_refresh_token(refresh_token_data["jti"], refresh_token_data["exp"] * 86400, refresh_token_data["sub"])

  result = await token_redis_repo.get_account_id(refresh_token_data["jti"])

  assert result == refresh_token_data["sub"]