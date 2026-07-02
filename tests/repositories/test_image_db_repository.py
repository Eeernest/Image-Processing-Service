import pytest

@pytest.mark.anyio
@pytest.mark.integration
async def test_save(image_db_repo, image_obj, saved_account_obj):
  result = await image_db_repo.save(image_obj)

  assert result.id is not None
  assert result.account_id == saved_account_obj.id