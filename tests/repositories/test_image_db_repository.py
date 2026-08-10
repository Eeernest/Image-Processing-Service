import pytest

from app.schemas.image_schema import ImageFormat

@pytest.mark.anyio
@pytest.mark.integration
async def test_save(image_db_repo, image_obj, saved_account_obj):
  result = await image_db_repo.save(image_obj)

  assert result.id is not None
  assert result.account_id == saved_account_obj.id

@pytest.mark.anyio
@pytest.mark.integration
async def test_get_by_id(image_db_repo, saved_image_obj):
  result = await image_db_repo.get_by_id(saved_image_obj.id, saved_image_obj.account_id)

  assert result == saved_image_obj

@pytest.mark.anyio
@pytest.mark.integration
async def test_get_all_by_account_id(image_db_repo, saved_image_obj):
  result = await image_db_repo.get_all_by_account_id(saved_image_obj.account_id, 0, 10)

  assert len(result) == 1
  assert saved_image_obj in result

@pytest.mark.anyio
@pytest.mark.integration
async def test_get_all_by_account_id_file_format(image_db_repo, saved_image_obj):
  result = await image_db_repo.get_all_by_account_id(saved_image_obj.account_id, 0, 10, ImageFormat.WEBP)

  assert len(result) == 0
  assert saved_image_obj not in result