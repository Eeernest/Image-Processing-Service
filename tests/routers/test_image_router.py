import pytest

from app.core.exceptions import UserNotFoundException, MaxFileSizeExceededException, ImageResolutionException, InvalidImageFormatException, ImageNotFoundException, S3DownloadFailedException, S3UploadFailedException, DuplicateImageException

@pytest.mark.anyio
@pytest.mark.unit
async def test_upload_image_success(image_obj, mock_image_service, unit_image_client, upload_file_payload):
  image_obj.id = 1

  mock_image_service.upload_image.return_value = image_obj

  result = await unit_image_client.post("/upload_image", files=upload_file_payload)
  data = result.json()

  assert result.status_code == 200
  assert data["filename"] == image_obj.filename
  assert data["file_size_bytes"] == image_obj.file_size_bytes

@pytest.mark.anyio
@pytest.mark.unit
async def test_upload_image_max_file_size_exception(mock_image_service, unit_image_client, upload_file_payload):
  mock_image_service.upload_image.side_effect = MaxFileSizeExceededException()

  result = await unit_image_client.post("/upload_image", files=upload_file_payload)
  data = result.json()

  assert result.status_code == 413
  assert data["detail"] == MaxFileSizeExceededException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_upload_image_resolution_exception(mock_image_service, unit_image_client, upload_file_payload):
  mock_image_service.upload_image.side_effect = ImageResolutionException()

  result = await unit_image_client.post("/upload_image", files=upload_file_payload)
  data = result.json()

  assert result.status_code == 400
  assert data["detail"] == ImageResolutionException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_upload_image_format_exception(mock_image_service, unit_image_client, upload_file_payload):
  mock_image_service.upload_image.side_effect = InvalidImageFormatException()

  result = await unit_image_client.post("/upload_image", files=upload_file_payload)
  data = result.json()

  assert result.status_code == 422
  assert data["detail"] == InvalidImageFormatException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_resize_image_success(image_obj, mock_image_service, unit_image_client, resize_file_params):
  image_obj.id = 1

  mock_image_service.resize_image.return_value = image_obj

  result = await unit_image_client.get("/resize_image/1", params=resize_file_params)
  data = result.json()

  assert result.status_code == 200
  assert data["id"] == image_obj.id

@pytest.mark.anyio
@pytest.mark.unit
async def test_resize_image_not_found_exception(mock_image_service, unit_image_client, resize_file_params):
  mock_image_service.resize_image.side_effect = ImageNotFoundException()

  result = await unit_image_client.get("/resize_image/12", params=resize_file_params)
  data = result.json()

  assert result.status_code == 404
  assert data["detail"] == ImageNotFoundException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_resize_image_user_not_found_exception(mock_image_service, unit_image_client, resize_file_params):
  mock_image_service.resize_image.side_effect = UserNotFoundException()

  result = await unit_image_client.get("/resize_image/21", params=resize_file_params)
  data = result.json()

  assert result.status_code == 404
  assert data["detail"] == UserNotFoundException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_resize_image_s3_download_exception(mock_image_service, unit_image_client, resize_file_params):
  mock_image_service.resize_image.side_effect = S3DownloadFailedException()

  result = await unit_image_client.get("/resize_image/1", params=resize_file_params)
  data = result.json()

  assert result.status_code == 503
  assert data["detail"] == S3DownloadFailedException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_resize_image_s3_upload_exception(mock_image_service, unit_image_client, resize_file_params):
  mock_image_service.resize_image.side_effect = S3UploadFailedException()

  result = await unit_image_client.get("/resize_image/1", params=resize_file_params)
  data = result.json()

  assert result.status_code == 503
  assert data["detail"] == S3UploadFailedException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_resize_image_race_condition(mock_image_service, unit_image_client, resize_file_params):
  mock_image_service.resize_image.side_effect = DuplicateImageException()

  result = await unit_image_client.get("/resize_image/2", params=resize_file_params)
  data = result.json()

  assert result.status_code == 409
  assert data["detail"] == DuplicateImageException.detail