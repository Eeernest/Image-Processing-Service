from io import BytesIO
from typing import BinaryIO

from botocore.exceptions import ClientError, BotoCoreError
from fastapi import UploadFile
from fastapi.concurrency import run_in_threadpool
from PIL import Image as PILImage, UnidentifiedImageError
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.exceptions import UserNotFoundException, MaxFileSizeExceededException, ImageResolutionException, InvalidImageFormatException, S3UploadFailedException, S3DownloadFailedException, DuplicateImageException, ImageNotFoundException, ImageTooSmallException
from app.models.image_model import Image
from app.repositories.image_db_repository import ImageDbRepository
from app.repositories.image_s3_repository import ImageS3Repository

class ImageService:
  def __init__(self, db_repo: ImageDbRepository, s3_repo: ImageS3Repository):
    self.db_repo = db_repo
    self.s3_repo = s3_repo

  async def upload_image(self, account_id: int, file: UploadFile) -> Image:
    filename = file.filename
    file_size_bytes = self._validate_file_size(file.size)
    content_type = file.content_type

    detected_format = await run_in_threadpool(self._validate_image, file.file)
    generated_key = f"account/{account_id}/images/{filename}"

    file.file.seek(0)

    image_obj = self._create_image_obj(account_id, filename, generated_key, file_size_bytes, detected_format)

    saved_image_obj = await self._try_save_image_obj(image_obj)

    await self._try_upload_to_s3(file.file, generated_key, content_type, saved_image_obj.id)

    return saved_image_obj

  async def resize_image(self, account_id: int, image_id: int, width: int, height: int) -> Image:
    image_obj = await self._try_get_image_obj_by_id(image_id)

    self._check_account_id(image_obj.account_id, account_id)

    file = await self._try_download_from_s3(image_obj.s3_key)

    resized_file = await run_in_threadpool(self._resize, file, width, height)

    filename = f"resized_{width}x{height}_{image_obj.filename}"
    generated_key = f"account/{image_obj.account_id}/images/{filename}"
    content_type = f"image/{str(image_obj.file_format).lower()}"

    resized_image_obj = self._create_image_obj(image_obj.account_id, filename, generated_key, len(resized_file.getvalue()), image_obj.file_format)

    saved_resized_image_obj = await self._try_save_image_obj(resized_image_obj)

    await self._try_upload_to_s3(resized_file, generated_key, content_type, saved_resized_image_obj.id)

    return saved_resized_image_obj

  async def crop_center_image(self, account_id: int, image_id: int, width: int, height: int) -> Image:
    image_obj = await self._try_get_image_obj_by_id(image_id)

    self._check_account_id(image_obj.account_id, account_id)

    file = await self._try_download_from_s3(image_obj.s3_key)

    cropped_file = await run_in_threadpool(self._crop_center, file, width, height)

    filename = f"cropped_{width}x{height}_{image_obj.filename}"
    generated_key = f"account/{image_obj.account_id}/images/{filename}"
    content_type = f"image{str(image_obj.file_format).lower()}"

    cropped_image_obj = self._create_image_obj(image_obj.account_id, filename, generated_key, len(cropped_file.getvalue()), image_obj.file_format)

    saved_cropped_image_obj = await self._try_save_image_obj(cropped_image_obj)

    await self._try_upload_to_s3(cropped_file, generated_key, content_type, saved_cropped_image_obj.id)

    return saved_cropped_image_obj



  async def _try_upload_to_s3(self, file: BinaryIO, generated_key: str, content_type: str, image_id) -> None:
    try:
      return await self.s3_repo.upload_to_s3(file, generated_key, content_type)

    except (ClientError, BotoCoreError):
      await self.db_repo.delete(image_id)

      raise S3UploadFailedException()

  async def _try_download_from_s3(self, s3_key: str) -> BytesIO:
    try:
      return await self.s3_repo.download_from_s3(s3_key)

    except (ClientError, BotoCoreError):
      raise S3DownloadFailedException()

  

  async def _try_save_image_obj(self, image_obj: Image) -> Image:
    try:
      return await self.db_repo.save(image_obj)

    except IntegrityError:
      raise DuplicateImageException()

  async def _try_get_image_obj_by_id(self, image_id: int) -> Image:
    image_obj = await self.db_repo.get_by_id(image_id)

    if image_obj is None:
      raise ImageNotFoundException()

    return image_obj

  
  def _check_account_id(self, image_obj_account_id: int, account_id: int) -> None:
    if image_obj_account_id != account_id:
      raise UserNotFoundException()

  def _create_image_obj(self, account_id: int, filename: str, s3_key: str, file_size_bytes: int, file_format: str) -> Image:
    return Image(
      account_id=account_id,
      filename=filename,
      s3_key=s3_key,
      file_size_bytes=file_size_bytes,
      file_format=file_format
    )

  

  def _validate_file_size(self, file_size: int) -> int:
    max_file_size = settings.MAX_FILE_SIZE

    if file_size > max_file_size:
      raise MaxFileSizeExceededException()

    return file_size
  
  def _validate_image(self, file) -> str:
    try:
      with PILImage.open(file) as img:
        allowed_image_formats = settings.ALLOWED_IMAGE_FOMRAT
        
        width, height = img.size

        if img.format.upper() not in allowed_image_formats:
          raise InvalidImageFormatException()

        if width > settings.MAX_IMAGE_WIDTH or height > settings.MAX_IMAGE_HEIGHT:
          raise ImageResolutionException()

        return img.format.upper()

    except UnidentifiedImageError:
      raise InvalidImageFormatException()

  def _resize(self, file: BinaryIO, width: int, height: int) -> BytesIO:
    with PILImage.open(file) as img:
      orig_width, orig_height = img.size

      if orig_width < width or orig_height < height:
        raise ImageTooSmallException()

      img.thumbnail((width, height), PILImage.Resampling.LANCZOS)

      output = BytesIO()

      img.save(output, format=img.format)

      output.seek(0)

      return output

  def _crop_center(self, file: BinaryIO, width: int, height: int) -> BytesIO:
    with PILImage.open(file) as img:
      orig_width, orig_height = img.size

      if orig_width < width or orig_height < height:
        raise ImageTooSmallException()

      left = (orig_width - width) // 2
      top = (orig_height - height) // 2
      right = (orig_width + width) // 2
      bottom = (orig_height + height) // 2

      cropped_img = img.crop((left, top, right, bottom))

      output = BytesIO()

      cropped_img.save(output, format=img.format)

      output.seek(0)

      return output