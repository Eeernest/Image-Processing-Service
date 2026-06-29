import pytest

from tests.fixtures.image_fixture import db_repo, image_obj

@pytest.mark.anyio
@pytest.mark.integration
async def test_save(db_repo, image_obj):
  result = await db_repo.save(image_obj)

  assert result.id is not None