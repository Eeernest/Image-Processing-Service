from botocore.exceptions import ClientError, BotoCoreError
from io import BytesIO
import pytest
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import MaxFileSizeExceededException, ImageResolutionException, InvalidImageFormatException, S3UploadFailedException, DuplicateImageException

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
async def test_upload_image_integrity_error(mock_image_db_repo, mock_image_s3_repo, image_service, mock_file):
  mock_image_s3_repo.upload_to_s3.return_value = None
  mock_image_db_repo.save.side_effect = IntegrityError("stmt", "params", "s3_key")
  mock_image_s3_repo.delete_from_s3.return_value = {"message": "Image deleted"}

  with pytest.raises(DuplicateImageException) as exc:
    await image_service.upload_image(1, mock_file)

  assert exc.value.status_code == DuplicateImageException.status_code
  assert exc.value.detail == DuplicateImageException.detail
  assert mock_image_s3_repo.delete_from_s3.call_count == 1