from io import BytesIO
from unittest.mock import AsyncMock, Mock

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
from app.schemas.image_schema import ImageFormat
from app.services.image_service import ImageService

@pytest.fixture()
def image_s3_repo(mocked_aws):
  return ImageS3Repository(mocked_aws)

@pytest.fixture()
def file_bytes():
  return b"fake_image_bytes"

@pytest.fixture()
def file_stream(file_bytes):
  return BytesIO(file_bytes)

@pytest.fixture()
def key():
  return "account/1/images/test_image.jpeg"

@pytest.fixture()
def image_db_repo(db_session):
  return ImageDbRepository(db_session)

@pytest.fixture()
def image_obj(saved_account_obj):
  return Image(
    account_id=saved_account_obj.id,
    filename="test.jpeg",
    s3_key="account/1/images/test.jpeg",
    file_format="JPEG",
    file_size_bytes=102450
  )

@pytest.fixture()
async def saved_image_obj(image_db_repo, image_obj):
  return await image_db_repo.save(image_obj)

@pytest.fixture()
def mock_image_db_repo():
  return AsyncMock()

@pytest.fixture()
def mock_image_s3_repo():
  mock = AsyncMock()
  mock.generate_url = Mock()

  return mock

@pytest.fixture()
def image_service(mock_image_db_repo, mock_image_s3_repo):
  return ImageService(mock_image_db_repo, mock_image_s3_repo)

@pytest.fixture()
def mock_file():
  img = PILImage.new("RGB", (100, 100), color="red")
  img_byte_arr = BytesIO()
  img.save(img_byte_arr, format="JPEG")
  real_image_bytes = img_byte_arr.getvalue()

  file = AsyncMock(spec=UploadFile)
  file.filename = "test.jpeg"
  file.content_type = "image/jpeg"
  file.read.return_value = real_image_bytes
  file.size = len(real_image_bytes)
  file.file = BytesIO(real_image_bytes)

  return file

@pytest.fixture()
def mock_file_like():
  img = PILImage.new("RGB", (100, 100), color="red")
  
  buffer = BytesIO()

  img.save(buffer, format="JPEG")

  buffer.seek(0)

  return buffer

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
  file.size = len(real_image_bytes)
  file.file = BytesIO(real_image_bytes)

  return file

@pytest.fixture()
def mock_image_url():
  return "mock_image_url"

@pytest.fixture()
def mock_image_obj_list(image_obj) -> list:
  second_image_obj = image_obj
  second_image_obj.file_format = ImageFormat.WEBP

  image_obj_list = [image_obj, second_image_obj]

  return image_obj_list

@pytest.fixture()
def integration_image_service(image_db_repo, image_s3_repo):
  return ImageService(image_db_repo, image_s3_repo)

@pytest.fixture()
def integration_image_current_user(saved_account_obj):
  return saved_account_obj

@pytest.fixture()
async def integration_image_client(integration_image_service, integration_image_current_user):
  app.dependency_overrides[get_image_service] = lambda: integration_image_service
  app.dependency_overrides[get_current_user] = lambda: integration_image_current_user

  async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
    yield c

  app.dependency_overrides.clear()

@pytest.fixture()
def sample_file_bytes():
  buffer = BytesIO()

  img = PILImage.new("RGB", (200, 100), color="blue")
  img.save(buffer, format="JPEG")

  buffer.seek(0)

  return buffer.getvalue()

@pytest.fixture()
def sample_file_bytes_resolution():
  buffer = BytesIO()

  img = PILImage.new("RGB", (50001, 100), color="blue")
  img.save(buffer, format="JPEG")

  buffer.seek(0)

  return buffer.getvalue()

@pytest.fixture()
async def uploaded_image(integration_image_client, sample_file_bytes):
  return await integration_image_client.post("/upload_image", files={"file": ("test.jpeg", sample_file_bytes, "image/jpeg")})