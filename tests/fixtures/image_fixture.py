import pytest

from app.models.image_model import Image
from app.repositories.image_db_repository import ImageDbRepository
from app.repositories.image_s3_repository import ImageS3Repository

@pytest.fixture()
def s3_repo(mocked_aws):
  return ImageS3Repository(mocked_aws)

@pytest.fixture()
def file_bytes():
  return b"fake_image_bytes"

@pytest.fixture()
def key():
  return "account/1/images/test_image.jpeg"

@pytest.fixture()
def db_repo(db_session):
  return ImageDbRepository(db_session)

@pytest.fixture()
def image_obj(saved_account_obj):
  account = saved_account_obj

  return Image(
    account_id=saved_account_obj.id,
    filename="test.jpg",
    s3_key="account/1/images/test.jpeg",
    file_format="JPEG",
    file_size_bytes=102450
  )