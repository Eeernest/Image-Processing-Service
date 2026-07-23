from botocore.exceptions import ClientError, BotoCoreError
from io import BytesIO
import pytest
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import UserNotFoundException, MaxFileSizeExceededException, ImageResolutionException, InvalidImageFormatException, S3UploadFailedException, DuplicateImageException, ImageNotFoundException, S3DownloadFailedException, ImageTooSmallException

@pytest.mark.anyio
@pytest.mark.unit
async def test_upload_image_success(image_obj, mock_image_db_repo, mock_image_s3_repo, image_service, mock_file):
  image_obj.id = 1

  mock_image_s3_repo.upload_to_s3.return_value = None
  mock_image_db_repo.save.return_value = image_obj

  result = await image_service.upload_image(image_obj.id, mock_file)

  assert result == image_obj
  assert mock_image_s3_repo.upload_to_s3.call_count == 1
  assert mock_image_db_repo.save.call_count == 1

@pytest.mark.anyio
@pytest.mark.unit
async def test_upload_image_max_file_size_exceeded_exception(image_service, mock_file):
  mock_file.size = 10 * 1024 * 1024 + 1
  mock_file.read.return_value = b"x" * mock_file.size

  with pytest.raises(MaxFileSizeExceededException) as exc:
    await image_service.upload_image(1, mock_file)

  assert exc.value.status_code == MaxFileSizeExceededException.status_code
  assert exc.value.detail == MaxFileSizeExceededException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_upload_image_resolution_exception(image_service, mock_invalid_file):
  with pytest.raises(ImageResolutionException) as exc:
    await image_service.upload_image(1, mock_invalid_file)

  assert exc.value.status_code == ImageResolutionException.status_code
  assert exc.value.detail == ImageResolutionException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_upload_image_invalid_image_format_exception(image_service, mock_invalid_file):
  invalid_bytes = b"fake_bytes"
  mock_invalid_file.read.return_value = invalid_bytes
  mock_invalid_file.file = BytesIO(invalid_bytes)

  with pytest.raises(InvalidImageFormatException) as exc:
    await image_service.upload_image(1, mock_invalid_file)

  assert exc.value.status_code == InvalidImageFormatException.status_code
  assert exc.value.detail == InvalidImageFormatException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_upload_image_client_error(mock_image_s3_repo, image_service, mock_file):
  mock_image_s3_repo.upload_to_s3.side_effect = ClientError({"Error": {"Code": "TestS3Error", "Message": "S3 upload failed"}}, "PutObject")

  with pytest.raises(S3UploadFailedException) as exc:
    await image_service.upload_image(1, mock_file)

  assert exc.value.status_code == S3UploadFailedException.status_code
  assert exc.value.detail == S3UploadFailedException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_upload_image_botocore_error(mock_image_s3_repo, image_service, mock_file):
  mock_image_s3_repo.upload_to_s3.side_effect = BotoCoreError()

  with pytest.raises(S3UploadFailedException) as exc:
    await image_service.upload_image(1, mock_file)

  assert exc.value.status_code == S3UploadFailedException.status_code
  assert exc.value.detail == S3UploadFailedException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_upload_image_race_condition(mock_image_db_repo, mock_image_s3_repo, image_service, mock_file):
  mock_image_s3_repo.upload_to_s3.return_value = None
  mock_image_db_repo.save.side_effect = IntegrityError("stmt", "params", "s3_key")
  mock_image_s3_repo.delete_from_s3.return_value = None

  with pytest.raises(DuplicateImageException) as exc:
    await image_service.upload_image(1, mock_file)

  assert exc.value.status_code == DuplicateImageException.status_code
  assert exc.value.detail == DuplicateImageException.detail
  assert mock_image_s3_repo.delete_from_s3.call_count == 1

@pytest.mark.anyio
@pytest.mark.unit
async def test_resize_image_success(image_obj, mock_image_db_repo, mock_image_s3_repo, image_service, mock_file_like):
  mock_image_db_repo.get_by_id.return_value = image_obj
  mock_image_s3_repo.download_from_s3.return_value = mock_file_like
  mock_image_s3_repo.upload_to_s3.return_value = None

  image_obj.filename = "resized_test.jpeg"

  mock_image_db_repo.save.return_value = image_obj

  result = await image_service.resize_image(image_obj.account_id, 1, 10, 10)

  assert result == image_obj
  assert mock_image_s3_repo.upload_to_s3.call_count == 1
  assert mock_image_db_repo.save.call_count == 1

@pytest.mark.anyio
@pytest.mark.unit
async def test_resize_image_not_found_exception(mock_image_db_repo, image_service):
  mock_image_db_repo.get_by_id.return_value = None

  with pytest.raises(ImageNotFoundException) as exc:
    await image_service.resize_image(1, 10, 4, 12)

  assert exc.value.status_code == ImageNotFoundException.status_code
  assert exc.value.detail == ImageNotFoundException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_resize_image_user_not_found_exception(image_obj, mock_image_db_repo, image_service):
  mock_image_db_repo.get_by_id.return_value = image_obj

  with pytest.raises(UserNotFoundException) as exc:
    await image_service.resize_image(12, 1, 100, 17)

  assert exc.value.status_code == UserNotFoundException.status_code
  assert exc.value.detail == UserNotFoundException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_resize_image_s3_download_exception(image_obj, mock_image_db_repo, mock_image_s3_repo, image_service):
  mock_image_db_repo.get_by_id.return_value = image_obj
  mock_image_s3_repo.download_from_s3.side_effect = BotoCoreError()

  with pytest.raises(S3DownloadFailedException) as exc:
    await image_service.resize_image(image_obj.account_id, 1, 10, 20)

  assert exc.value.status_code == S3DownloadFailedException.status_code
  assert exc.value.detail == S3DownloadFailedException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_resize_image_too_small_exception(image_obj, mock_image_db_repo, mock_image_s3_repo, image_service, mock_file_like):
  mock_image_db_repo.get_by_id.return_value = image_obj
  mock_image_s3_repo.download_from_s3.return_value = mock_file_like

  with pytest.raises(ImageTooSmallException) as exc:
    await image_service.resize_image(image_obj.account_id, 1, 1000, 2000)

  assert exc.value.status_code == ImageTooSmallException.status_code
  assert exc.value.detail == ImageTooSmallException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_resize_image_s3_upload_exception(image_obj, mock_image_db_repo, mock_image_s3_repo, image_service, mock_file_like):
  mock_image_db_repo.get_by_id.return_value = image_obj
  mock_image_s3_repo.download_from_s3.return_value = mock_file_like
  mock_image_s3_repo.upload_to_s3.side_effect = BotoCoreError()

  with pytest.raises(S3UploadFailedException) as exc:
    await image_service.resize_image(image_obj.account_id, 1, 20, 14)

  assert exc.value.status_code == S3UploadFailedException.status_code
  assert exc.value.detail == S3UploadFailedException.detail
  assert mock_image_s3_repo.upload_to_s3.call_count == 1

@pytest.mark.anyio
@pytest.mark.unit
async def test_resize_image_race_condition(image_obj, mock_image_db_repo, mock_image_s3_repo, image_service, mock_file_like):
  mock_image_db_repo.get_by_id.return_value = image_obj
  mock_image_s3_repo.download_from_s3.return_value = mock_file_like
  mock_image_s3_repo.upload_to_s3.return_value = None
  mock_image_db_repo.save.side_effect = IntegrityError("stmt", "params", "s3_key")
  mock_image_s3_repo.delete_from_s3.return_value = None

  with pytest.raises(DuplicateImageException) as exc:
    await image_service.resize_image(image_obj.account_id, 1, 11, 12)

  assert exc.value.status_code == DuplicateImageException.status_code
  assert exc.value.detail == DuplicateImageException.detail
  assert mock_image_s3_repo.upload_to_s3.call_count == 1
  assert mock_image_db_repo.save.call_count == 1