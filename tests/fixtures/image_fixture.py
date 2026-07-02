from io import BytesIO
from unittest.mock import AsyncMock

from fastapi import UploadFile
from PIL import Image as PILImage
import pytest

from app.models.image_model import Image
from app.repositories.image_db_repository import ImageDbRepository
from app.repositories.image_s3_repository import ImageS3Repository
from app.services.image_service import ImageService

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

@pytest.fixture()
def mock_image_db_repo():
  return AsyncMock()

@pytest.fixture()
def mock_image_s3_repo():
  return AsyncMock()

@pytest.fixture()
def image_service(mock_image_db_repo, mock_image_s3_repo):
  return ImageService(mock_image_db_repo, mock_image_s3_repo)

@pytest.fixture()
def mock_file():
  img = PILImage.new("RGB", (1, 1), color="red")
  img_byte_arr = BytesIO()
  img.save(img_byte_arr, format="JPEG")
  real_image_bytes = img_byte_arr.getvalue()

  file = AsyncMock(spec=UploadFile)
  file.filename = "test.jpeg"
  file.content_type = "image/jpeg"
  file.read.return_value = real_image_bytes

  return file

@pytest.fixture()
def mock_invalid_file():
  img = PILImage.new("RGB", (5001, 5001), color="red")
  img_byte_arr = BytesIO()
  img.save(img_byte_arr, format="JPEG")
  real_image_bytes = img_byte_arr.getvalue()

  file = AsyncMock(spec=UploadFile)
  file.filename = "test.jpeg"
  file.content_type = "image/jpeg"
  file.read.return_value = real_image_bytes

  return file