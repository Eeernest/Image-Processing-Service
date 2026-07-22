from io import BytesIO

from botocore.exceptions import ClientError, BotoCoreError
from fastapi import UploadFile
from fastapi.concurrency import run_in_threadpool
from PIL import Image as PILImage, UnidentifiedImageError
from sqlalchemy.exc import IntegrityError

from app.core.config import settings
from app.core.exceptions import MaxFileSizeExceededException, ImageResolutionException, InvalidImageFormatException, S3UploadFailedException, DuplicateImageException, ImageNotFoundException
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

    try:
      await self.s3_repo.upload_to_s3(file.file, generated_key, content_type)

    except (ClientError,BotoCoreError):
      raise S3UploadFailedException()

    image_obj = Image(
      account_id=account_id,
      filename=filename,
      s3_key=generated_key,
      file_size_bytes=file_size_bytes,
      file_format=detected_format
    )

    try:
      return await self.db_repo.save(image_obj)

    except IntegrityError:
      await self.s3_repo.delete_from_s3(generated_key)

      raise DuplicateImageException()

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
