import pytest

from app.repositories.image_s3_repository import ImageS3Repository

@pytest.fixture()
def s3_repo(mocked_aws):
  return ImageS3Repository(mocked_aws)

@pytest.fixture()
def file_bytes():
  return b"fake_image_bytes"

@pytest.fixture()
def key():
  return "uploads/test_image/image.jpg"