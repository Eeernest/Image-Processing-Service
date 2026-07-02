from io import BytesIO

from botocore.exceptions import ClientError, BotoCoreError
from fastapi import UploadFile
from PIL import Image as PILImage, UnidentifiedImageError
from sqlalchemy.exc import IntegrityError

from app.core.exceptions import MaxFileSizeExceededException, ImageResolutionException, InvalidImageFormatException, S3UploadFailedException, DuplicateImageException
from app.models.image_model import Image
from app.repositories.image_db_repository import ImageDbRepository
from app.repositories.image_s3_repository import ImageS3Repository

class ImageService:
  def __init__(self, db_repo: ImageDbRepository, s3_repo: ImageS3Repository):
    self.db_repo = db_repo
    self.s3_repo = s3_repo

  def _validate_file_size(self, file_bytes: bytes) -> int:
    max_file_size = 10 * 1024 * 1024

    file_size_bytes = len(file_bytes)

    if file_size_bytes > max_file_size:
      raise MaxFileSizeExceededException()

    return file_size_bytes

  def _validate_image(self, file_bytes: bytes) -> None:
    try:
      with PILImage.open(BytesIO(file_bytes)) as img:
        allowed_image_formats = ["PNG", "JPEG", "WEBP"]
        max_width = 5000
        max_height = 5000

        width, height = img.size

        if img.format.upper() not in allowed_image_formats:
          raise InvalidImageFormatException()

        if width > max_width or height > max_height:
          raise ImageResolutionException()

    except UnidentifiedImageError:
      raise InvalidImageFormatException()

  async def upload_image(self, account_id: int, file: UploadFile) -> Image:
    filename = file.filename
    file_bytes = await file.read()
    file_size_bytes = self._validate_file_size(file_bytes)
    content_type = file.content_type

    self._validate_image(file_bytes)

    generated_key = f"account/{account_id}/images/{filename}"

    try:
      await self.s3_repo.upload_to_s3(file_bytes, generated_key, content_type)

    except (ClientError,BotoCoreError):
      raise S3UploadFailedException()

    image_obj = Image(
      account_id=account_id,
      filename=filename,
      s3_key=generated_key,
      file_size_bytes=file_size_bytes
    )

    try:
      return await self.db_repo.save(image_obj)

    except IntegrityError:
      await self.s3_repo.delete_from_s3(generated_key)

      raise DuplicateImageException()