import pytest

import app.core.exceptions as e
from app.schemas.image_schema import ImageFormat

@pytest.mark.anyio
@pytest.mark.integration
async def test_upload_image_success(integration_image_client, sample_file_bytes):
  result = await integration_image_client.post("/upload_image", files={"file": ("test.jpeg", sample_file_bytes, "image/jpeg")})

  assert result.status_code == 200

@pytest.mark.anyio
@pytest.mark.integration
async def test_upload_image_max_file_szie_eception(integration_image_client):
  result = await integration_image_client.post("/upload_image", files={"file": ("test.jpeg", b"0" * (11 * 1024 * 1024), "image/jpeg")})
  data = result.json()

  assert result.status_code == e.MaxFileSizeExceededException.status_code
  assert data["detail"] == e.MaxFileSizeExceededException.detail

@pytest.mark.anyio
@pytest.mark.integration
async def test_upload_image_resolution_exception(integration_image_client, sample_file_bytes_resolution):
  result = await integration_image_client.post("/upload_image", files={"file": ("test.jpeg", sample_file_bytes_resolution, "image/jpeg")})
  data = result.json()

  assert result.status_code == e.ImageResolutionException.status_code
  assert data["detail"] == e.ImageResolutionException.detail

@pytest.mark.anyio
@pytest.mark.integration
async def test_resize_image_success(integration_image_client, uploaded_image):
  image_data = uploaded_image.json()

  result = await integration_image_client.get(f"/resize_image/{image_data["id"]}", params={"width": 20, "height": 20})

  assert result.status_code == 200

@pytest.mark.anyio
@pytest.mark.integration
async def test_resize_image_too_small_exception(integration_image_client, uploaded_image):
  image_data = uploaded_image.json()

  result = await integration_image_client.get(f"/resize_image/{image_data["id"]}", params={"width": 400, "height": 21})
  data = result.json()

  assert result.status_code == e.ImageTooSmallException.status_code
  assert data["detail"] == e.ImageTooSmallException.detail

@pytest.mark.anyio
@pytest.mark.integration
async def test_crop_center_image_success(integration_image_client, uploaded_image):
  image_data = uploaded_image.json()

  result = await integration_image_client.get(f"/crop_center_image/{image_data["id"]}", params={"width": 40, "height": 50})

  assert result.status_code == 200

@pytest.mark.anyio
@pytest.mark.integration
async def test_crop_center_image_too_small_exception(integration_image_client, uploaded_image):
  image_data = uploaded_image.json()
  
  result = await integration_image_client.get(f"/crop_center_image/{image_data["id"]}", params={"width": 201, "height": 50})
  data = result.json()

  assert result.status_code == e.ImageTooSmallException.status_code
  assert data["detail"] == e.ImageTooSmallException.detail

@pytest.mark.anyio
@pytest.mark.integration
async def test_change_image_format_success(integration_image_client, uploaded_image):
  image_data = uploaded_image.json()

  result = await integration_image_client.get(f"/change_image_format/{image_data["id"]}", params={"format": ImageFormat.WEBP.value})

  assert result.status_code == 200

@pytest.mark.anyio
@pytest.mark.unit
async def test_change_image_format_same_format_exception(integration_image_client, uploaded_image):
  image_data = uploaded_image.json()

  result = await integration_image_client.get(f"/change_image_format/{image_data["id"]}", params={"format": ImageFormat.JPEG.value})
  data = result.json()

  assert result.status_code == e.ImageSameFormatException.status_code
  assert data["detail"] == e.ImageSameFormatException.detail