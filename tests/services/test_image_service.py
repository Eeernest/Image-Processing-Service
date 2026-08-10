from botocore.exceptions import ClientError, BotoCoreError, NoCredentialsError
from io import BytesIO
import pytest
from sqlalchemy.exc import IntegrityError

import app.core.exceptions as e
from app.schemas.image_schema import ImageFormat

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

  with pytest.raises(e.MaxFileSizeExceededException) as exc:
    await image_service.upload_image(1, mock_file)

  assert exc.value.status_code == e.MaxFileSizeExceededException.status_code
  assert exc.value.detail == e.MaxFileSizeExceededException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_upload_image_resolution_exception(image_service, mock_invalid_file):
  with pytest.raises(e.ImageResolutionException) as exc:
    await image_service.upload_image(1, mock_invalid_file)

  assert exc.value.status_code == e.ImageResolutionException.status_code
  assert exc.value.detail == e.ImageResolutionException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_upload_image_invalid_image_format_exception(image_service, mock_invalid_file):
  invalid_bytes = b"fake_bytes"
  mock_invalid_file.read.return_value = invalid_bytes
  mock_invalid_file.file = BytesIO(invalid_bytes)

  with pytest.raises(e.InvalidImageFormatException) as exc:
    await image_service.upload_image(1, mock_invalid_file)

  assert exc.value.status_code == e.InvalidImageFormatException.status_code
  assert exc.value.detail == e.InvalidImageFormatException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_upload_image_client_error(mock_image_s3_repo, image_service, mock_file):
  mock_image_s3_repo.upload_to_s3.side_effect = ClientError({"Error": {"Code": "TestS3Error", "Message": "S3 upload failed"}}, "PutObject")

  with pytest.raises(e.S3UploadFailedException) as exc:
    await image_service.upload_image(1, mock_file)

  assert exc.value.status_code == e.S3UploadFailedException.status_code
  assert exc.value.detail == e.S3UploadFailedException.detail
  assert mock_image_s3_repo.upload_to_s3.call_count == 1

@pytest.mark.anyio
@pytest.mark.unit
async def test_upload_image_botocore_error(mock_image_s3_repo, image_service, mock_file):
  mock_image_s3_repo.upload_to_s3.side_effect = BotoCoreError()

  with pytest.raises(e.S3UploadFailedException) as exc:
    await image_service.upload_image(1, mock_file)

  assert exc.value.status_code == e.S3UploadFailedException.status_code
  assert exc.value.detail == e.S3UploadFailedException.detail
  assert mock_image_s3_repo.upload_to_s3.call_count == 1

@pytest.mark.anyio
@pytest.mark.unit
async def test_upload_image_race_condition(mock_image_db_repo, mock_image_s3_repo, image_service, mock_file):
  mock_image_s3_repo.uplaod_to_s3.return_value = None
  mock_image_db_repo.save.side_effect = IntegrityError("stmt", "params", "s3_key")
  mock_image_s3_repo.delete_from_s3.return_value = None

  with pytest.raises(e.DuplicateImageException) as exc:
    await image_service.upload_image(1, mock_file)

  assert exc.value.status_code == e.DuplicateImageException.status_code
  assert exc.value.detail == e.DuplicateImageException.detail
  assert mock_image_s3_repo.upload_to_s3.call_count == 1
  assert mock_image_db_repo.save.call_count == 1
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

  with pytest.raises(e.ImageNotFoundException) as exc:
    await image_service.resize_image(1, 10, 4, 12)

  assert exc.value.status_code == e.ImageNotFoundException.status_code
  assert exc.value.detail == e.ImageNotFoundException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_resize_image_s3_download_exception(image_obj, mock_image_db_repo, mock_image_s3_repo, image_service):
  mock_image_db_repo.get_by_id.return_value = image_obj
  mock_image_s3_repo.download_from_s3.side_effect = BotoCoreError()

  with pytest.raises(e.S3DownloadFailedException) as exc:
    await image_service.resize_image(image_obj.account_id, 1, 10, 20)

  assert exc.value.status_code == e.S3DownloadFailedException.status_code
  assert exc.value.detail == e.S3DownloadFailedException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_resize_image_too_small_exception(image_obj, mock_image_db_repo, mock_image_s3_repo, image_service, mock_file_like):
  mock_image_db_repo.get_by_id.return_value = image_obj
  mock_image_s3_repo.download_from_s3.return_value = mock_file_like

  with pytest.raises(e.ImageTooSmallException) as exc:
    await image_service.resize_image(image_obj.account_id, 1, 1000, 2000)

  assert exc.value.status_code == e.ImageTooSmallException.status_code
  assert exc.value.detail == e.ImageTooSmallException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_resize_image_s3_upload_exception(image_obj, mock_image_db_repo, mock_image_s3_repo, image_service, mock_file_like):
  mock_image_db_repo.get_by_id.return_value = image_obj
  mock_image_s3_repo.download_from_s3.return_value = mock_file_like
  mock_image_s3_repo.upload_to_s3.side_effect = BotoCoreError()

  with pytest.raises(e.S3UploadFailedException) as exc:
    await image_service.resize_image(image_obj.account_id, 1, 20, 14)

  assert exc.value.status_code == e.S3UploadFailedException.status_code
  assert exc.value.detail == e.S3UploadFailedException.detail
  assert mock_image_s3_repo.upload_to_s3.call_count == 1

@pytest.mark.anyio
@pytest.mark.unit
async def test_resize_image_race_condition(image_obj, mock_image_db_repo, mock_image_s3_repo, image_service, mock_file_like):
  mock_image_db_repo.get_by_id.return_value = image_obj
  mock_image_s3_repo.download_from_s3.return_value = mock_file_like
  mock_image_s3_repo.upload_to_s3.return_value = None
  mock_image_db_repo.save.side_effect = IntegrityError("stmt", "params", "s3_key")
  mock_image_s3_repo.delete_from_s3.return_value = None

  with pytest.raises(e.DuplicateImageException) as exc:
    await image_service.resize_image(image_obj.account_id, 1, 11, 12)

  assert exc.value.status_code == e.DuplicateImageException.status_code
  assert exc.value.detail == e.DuplicateImageException.detail
  assert mock_image_s3_repo.upload_to_s3.call_count == 1
  assert mock_image_db_repo.save.call_count == 1
  assert mock_image_s3_repo.delete_from_s3.call_count == 1

@pytest.mark.anyio
@pytest.mark.unit
async def test_crop_center_image_success(image_obj, mock_image_db_repo, mock_image_s3_repo, image_service, mock_file_like):
  mock_image_db_repo.get_by_id.return_value = image_obj
  mock_image_s3_repo.download_from_s3.return_value = mock_file_like
  mock_image_s3_repo.upload_to_s3.return_value = None
  mock_image_db_repo.save.return_value = image_obj

  result = await image_service.crop_center_image(image_obj.account_id, 1, 12, 34)

  assert result == image_obj
  assert mock_image_s3_repo.upload_to_s3.call_count == 1
  assert mock_image_db_repo.save.call_count == 1

@pytest.mark.anyio
@pytest.mark.unit
async def test_crop_center_image_not_found_exception(mock_image_db_repo, image_service):
  mock_image_db_repo.get_by_id.side_effect = e.ImageNotFoundException()

  with pytest.raises(e.ImageNotFoundException) as exc:
    await image_service.crop_center_image(1, 12, 34, 34)

  assert exc.value.status_code == e.ImageNotFoundException.status_code
  assert exc.value.detail == e.ImageNotFoundException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_crop_center_image_s3_download_s3_exception(image_obj, mock_image_db_repo, mock_image_s3_repo, image_service):
  mock_image_db_repo.get_by_id.return_value = image_obj
  mock_image_s3_repo.download_from_s3.side_effect = e.S3DownloadFailedException()

  with pytest.raises(e.S3DownloadFailedException) as exc:
    await image_service.crop_center_image(image_obj.account_id, 1, 12, 23)

  assert exc.value.status_code == e.S3DownloadFailedException.status_code
  assert exc.value.detail == e.S3DownloadFailedException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_crop_center_image_too_small_exception(image_obj, mock_image_db_repo, mock_image_s3_repo, image_service, mock_file_like):
  mock_image_db_repo.get_by_id.return_value = image_obj
  mock_image_s3_repo.download_from_s3.return_value = mock_file_like

  with pytest.raises(e.ImageTooSmallException) as exc:
    await image_service.crop_center_image(image_obj.account_id, 1, 200, 300)

  assert exc.value.status_code == e.ImageTooSmallException.status_code
  assert exc.value.detail == e.ImageTooSmallException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_crop_center_image_s3_upload_exception(image_obj, mock_image_db_repo, mock_image_s3_repo, image_service, mock_file_like):
  mock_image_db_repo.get_by_id.return_value = image_obj
  mock_image_s3_repo.download_from_s3.return_value = mock_file_like
  mock_image_s3_repo.upload_to_s3.side_effect = e.S3UploadFailedException()

  with pytest.raises(e.S3UploadFailedException) as exc:
    await image_service.crop_center_image(image_obj.account_id, 12, 33, 33)

  assert exc.value.status_code == e.S3UploadFailedException.status_code
  assert exc.value.detail == e.S3UploadFailedException.detail
  assert mock_image_s3_repo.upload_to_s3.call_count == 1

@pytest.mark.anyio
@pytest.mark.unit
async def test_crop_center_image_race_condition(image_obj, mock_image_db_repo, mock_image_s3_repo, image_service, mock_file_like):
  mock_image_db_repo.get_by_id.return_value = image_obj
  mock_image_s3_repo.download_from_s3.return_value = mock_file_like
  mock_image_s3_repo.upload_to_s3.return_value = None
  mock_image_db_repo.save.side_effect = IntegrityError("stmt", "params", "s3_key")
  mock_image_s3_repo.delete_from_s3.return_value = None

  with pytest.raises(e.DuplicateImageException) as exc:
    await image_service.crop_center_image(image_obj.account_id, 1, 34, 12)

  assert exc.value.status_code == e.DuplicateImageException.status_code
  assert exc.value.detail == e.DuplicateImageException.detail
  assert mock_image_s3_repo.upload_to_s3.call_count == 1
  assert mock_image_db_repo.save.call_count == 1
  assert mock_image_s3_repo.delete_from_s3.call_count == 1

@pytest.mark.anyio
@pytest.mark.unit
async def test_change_image_format_success(image_obj, mock_image_db_repo, mock_image_s3_repo, image_service, mock_file_like):
  mock_image_db_repo.get_by_id.return_value = image_obj
  mock_image_s3_repo.download_from_s3.return_value = mock_file_like

  image_obj.file_format = ImageFormat.PNG

  mock_image_s3_repo.upload_to_s3.return_value = None
  mock_image_db_repo.save.return_value = image_obj

  result = await image_service.change_image_format(image_obj.account_id, 1, ImageFormat.PNG)

  assert result.file_format == ImageFormat.PNG
  assert mock_image_s3_repo.upload_to_s3.call_count == 1
  assert mock_image_db_repo.save.call_count == 1

@pytest.mark.anyio
@pytest.mark.unit
async def test_change_image_format_image_not_found_exception(mock_image_db_repo, image_service):
  mock_image_db_repo.get_by_id.side_effect = e.ImageNotFoundException()

  with pytest.raises(e.ImageNotFoundException) as exc:
    await image_service.change_image_format(1, 1, ImageFormat.JPEG)

  assert exc.value.status_code == e.ImageNotFoundException.status_code
  assert exc.value.detail == e.ImageNotFoundException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_change_image_format_s3_download_exception(image_obj, mock_image_db_repo, mock_image_s3_repo, image_service):
  mock_image_db_repo.get_by_id.return_value = image_obj
  mock_image_s3_repo.download_from_s3.side_effect = e.S3DownloadFailedException()

  with pytest.raises(e.S3DownloadFailedException) as exc:
    await image_service.change_image_format(image_obj.account_id, 34, ImageFormat.WEBP)

  assert exc.value.status_code == e.S3DownloadFailedException.status_code
  assert exc.value.detail == e.S3DownloadFailedException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_change_image_format_same_format_exception(image_obj, mock_image_db_repo, mock_image_s3_repo, image_service, mock_file_like):
  mock_image_db_repo.get_by_id.return_value = image_obj
  mock_image_s3_repo.download_from_s3.return_value = mock_file_like

  with pytest.raises(e.ImageSameFormatException) as exc:
    await image_service.change_image_format(image_obj.account_id, 1, ImageFormat.JPEG)

  assert exc.value.status_code == e.ImageSameFormatException.status_code
  assert exc.value.detail == e.ImageSameFormatException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_change_image_format_s3_upload_exception(image_obj, mock_image_db_repo, mock_image_s3_repo, image_service, mock_file_like):
  mock_image_db_repo.get_by_id.return_value = image_obj
  mock_image_s3_repo.download_from_s3.return_value = mock_file_like
  mock_image_s3_repo.upload_to_s3.side_effect = BotoCoreError()

  with pytest.raises(e.S3UploadFailedException) as exc:
    await image_service.change_image_format(image_obj.account_id, 2, ImageFormat.PNG)

  assert exc.value.status_code == e.S3UploadFailedException.status_code
  assert exc.value.detail == e.S3UploadFailedException.detail
  assert mock_image_s3_repo.upload_to_s3.call_count == 1

@pytest.mark.anyio
@pytest.mark.unit
async def test_change_image_format_race_condition(image_obj, mock_image_db_repo, mock_image_s3_repo, image_service, mock_file_like):
  mock_image_db_repo.get_by_id.return_value = image_obj
  mock_image_s3_repo.download_from_s3.return_value = mock_file_like
  mock_image_s3_repo.upload_to_s3.return_value = None
  mock_image_db_repo.save.side_effect = IntegrityError("stmt", "params", "s3_key")
  mock_image_s3_repo.delete_from_s3.return_value = None

  with pytest.raises(e.DuplicateImageException) as exc:
    await image_service.change_image_format(image_obj.account_id, 1, ImageFormat.WEBP)

  assert exc.value.status_code == e.DuplicateImageException.status_code
  assert exc.value.detail == e.DuplicateImageException.detail
  assert mock_image_s3_repo.upload_to_s3.call_count == 1
  assert mock_image_db_repo.save.call_count == 1
  assert mock_image_s3_repo.delete_from_s3.call_count == 1


@pytest.mark.anyio
@pytest.mark.unit
async def test_generate_image_url_success(image_obj, mock_image_db_repo, mock_image_s3_repo, image_service, mock_image_url):
  mock_image_db_repo.get_by_id.return_value = image_obj
  mock_image_s3_repo.generate_url.return_value = mock_image_url

  result = await image_service.generate_image_url(image_obj.account_id, 1)

  assert result == mock_image_url

@pytest.mark.anyio
@pytest.mark.unit
async def test_generate_image_url_image_not_found_exception(mock_image_db_repo, image_service):
  mock_image_db_repo.get_by_id.side_effect = e.ImageNotFoundException

  with pytest.raises(e.ImageNotFoundException) as exc:
    await image_service.generate_image_url(1, 1)

  assert exc.value.status_code == e.ImageNotFoundException.status_code
  assert exc.value.detail == e.ImageNotFoundException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_generate_image_url_no_credentials_exceptions(image_obj, mock_image_db_repo, mock_image_s3_repo, image_service):
  mock_image_db_repo.get_by_id.return_value = image_obj
  mock_image_s3_repo.generate_url.side_effect = NoCredentialsError()

  with pytest.raises(e.S3NoCredentialsException) as exc:
    await image_service.generate_image_url(image_obj.account_id, 34)

  assert exc.value.status_code == e.S3NoCredentialsException.status_code
  assert exc.value.detail == e.S3NoCredentialsException.detail

@pytest.mark.anyio
@pytest.mark.unit
async def test_view_uploaded_images_no_format_success(mock_image_db_repo, image_service, mock_image_obj_list):
  mock_image_db_repo.get_by_account_id.return_value = mock_image_obj_list[0]
  mock_image_db_repo.get_all_by_account_id.return_value = mock_image_obj_list

  result = await image_service.view_uploaded_images(mock_image_obj_list[0].account_id, 0, 10)

  assert len(result) == 2

@pytest.mark.anyio
@pytest.mark.unit
async def test_view_uploaded_images_format_success(mock_image_db_repo, image_service, mock_image_obj_list):
  mock_image_db_repo.get_by_account_id.return_value = mock_image_obj_list[0]
  mock_image_db_repo.get_all_by_account_id.return_value = [mock_image_obj_list[1]]

  result = await image_service.view_uploaded_images(mock_image_obj_list[0].account_id, 0, 10, ImageFormat.WEBP)

  assert len(result) == 1
  assert mock_image_obj_list[1] in result