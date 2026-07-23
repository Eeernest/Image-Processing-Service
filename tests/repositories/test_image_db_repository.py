import pytest

@pytest.mark.anyio
@pytest.mark.integration
async def test_save(image_db_repo, image_obj, saved_account_obj):
  result = await image_db_repo.save(image_obj)

  assert result.id is not None
  assert result.account_id == saved_account_obj.id

@pytest.mark.anyio
@pytest.mark.integration
async def test_get_by_id(image_db_repo, saved_image_obj):
  result = await image_db_repo.get_by_id(saved_image_obj.id)

  assert result == saved_image_obj