import pytest

@pytest.mark.anyio
@pytest.mark.integration
async def test_store_and_delete_refresh_token_success(token_redis_repo, refresh_token_data):
  await token_redis_repo.store_refresh_token(refresh_token_data["jti"], refresh_token_data["exp"] * 86400, refresh_token_data["sub"])

  stored_token = await token_redis_repo.get_account_id(refresh_token_data["jti"])

  assert stored_token == refresh_token_data["sub"]

  await token_redis_repo.delete_refresh_token(refresh_token_data["jti"])

  deleted_token = await token_redis_repo.get_account_id(refresh_token_data["jti"])

  assert deleted_token == None