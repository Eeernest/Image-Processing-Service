from io import BytesIO
from unittest.mock import AsyncMock

from fastapi import UploadFile
from httpx import AsyncClient, ASGITransport
from PIL import Image as PILImage
import pytest

from app.dependencies.image_dependency import get_image_service
from app.dependencies.permit_dependency import get_current_user
from app.main import app
from app.models.image_model import Image
from app.repositories.image_db_repository import ImageDbRepository
from app.repositories.image_s3_repository import ImageS3Repository
from app.services.image_service import ImageService

@pytest.fixture()
def image_s3_repo(mocked_aws):
  return ImageS3Repository(mocked_aws)

@pytest.fixture()
def file_bytes():
  return b"fake_image_bytes"

@pytest.fixture()
def key():
  return "account/1/images/test_image.jpeg"

@pytest.fixture()
def image_db_repo(db_session):
  return ImageDbRepository(db_session)

@pytest.fixture()
def image_obj(saved_account_obj):
  account = saved_account_obj

  return Image(
    account_id=saved_account_obj.id,
    filename="test.jpeg",
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

@pytest.fixture()
def mock_image_service():
  return AsyncMock()

@pytest.fixture()
def mock_image_current_user():
  return AsyncMock()

@pytest.fixture()
async def unit_image_client(mock_image_service, mock_image_current_user):
  app.dependency_overrides[get_image_service] = lambda: mock_image_service
  app.dependency_overrides[get_current_user] = lambda: mock_image_current_user

  async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
    yield c

  app.dependency_overrides.clear()

@pytest.fixture
def file_payload():
  return {"file": ("test.jpeg", b"data", "image/jpeg")}


@pytest.fixture()
def integration_image_service(image_db_repo, image_s3_repo):
  return ImageService(image_db_repo, image_s3_repo)