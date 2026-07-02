import pytest

from app.core.exceptions import MaxFileSizeExceededException, ImageResolutionException, InvalidImageFormatException

@pytest.mark.anyio
@pytest.mark.unit
async def test_upload_image_success(image_obj, mock_image_service, unit_image_client, file_payload):
  mock_image_service.upload_image.return_value = image_obj

  result = await unit_image_client.post("/upload_image", files=file_payload)
  data = result.json()

  assert result.status_code == 200
  assert data["filename"] == image_obj.filename
  assert data["file_size_bytes"] == image_obj.file_size_bytes

@pytest.mark.anyio
@pytest.mark.unit
async def test_upload_image_max_file_size_exception(mock_image_service, unit_image_client, file_payload):
  mock_image_service.upload_image.side_effect = MaxFileSizeExceededException()

  result = await unit_image_client.post("/upload_image", files=file_payload)
  data = result.json()

  assert result.status_code == 413
  assert data["detail"] == MaxFileSizeExceededException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_upload_image_resolution_exception(mock_image_service, unit_image_client, file_payload):
  mock_image_service.upload_image.side_effect = ImageResolutionException()

  result = await unit_image_client.post("/upload_image", files=file_payload)
  data = result.json()

  assert result.status_code == 400
  assert data["detail"] == ImageResolutionException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_upload_image_format_exception(mock_image_service, unit_image_client, file_payload):
  mock_image_service.upload_image.side_effect = InvalidImageFormatException()

  result = await unit_image_client.post("/upload_image", files=file_payload)
  data = result.json()

  assert result.status_code == 422
  assert data["detail"] == InvalidImageFormatException.detail