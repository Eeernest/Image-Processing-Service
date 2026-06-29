from io import BytesIO
import mimetypes

from fastapi.concurrency import run_in_threadpool
from types_boto3_s3 import S3Client

from app.core.config import settings

class ImageS3Repository:
  def __init__(self, s3_client: S3Client):
    self.s3_client = s3_client

  async def upload_to_s3(self, file_bytes: bytes, key: str, content_type: str | None = None) -> None:
    if content_type is None:
      content_type = mimetypes.guess_type(key)[0] or "image/jpeg"

    await run_in_threadpool(
      self.s3_client.upload_fileobj,
      BytesIO(file_bytes),
      settings.S3_BUCKET_NAME,
      key,
      ExtraArgs={"ContentType": content_type}
    )