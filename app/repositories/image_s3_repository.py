from io import BytesIO
from typing import BinaryIO

from botocore.exceptions import ClientError, BotoCoreError
from fastapi.concurrency import run_in_threadpool
from types_boto3_s3 import S3Client

from app.core.config import settings

class ImageS3Repository:
  def __init__(self, s3_client: S3Client):
    self.s3_client = s3_client

  async def upload_to_s3(self, file: BinaryIO, key: str, content_type: str | None = None) -> None:
    file.seek(0)

    try:
      await run_in_threadpool(
        self.s3_client.upload_fileobj,
        file,
        settings.S3_BUCKET_NAME,
        key,
        ExtraArgs={"ContentType": content_type}
      )

    except (ClientError, BotoCoreError) as exc:
      raise exc

  async def delete_from_s3(self, key: str) -> None:
    await run_in_threadpool(
      self.s3_client.delete_object,
      Bucket=settings.S3_BUCKET_NAME,
      Key=key
    )

  async def download_from_s3(self, key: str) -> BytesIO:
    buffer = BytesIO()

    try:
      await run_in_threadpool(
        self.s3_client.download_fileobj,
        settings.S3_BUCKET_NAME,
        key,
        buffer
      )

      buffer.seek(0)

      return buffer

    except (ClientError, BotoCoreError) as exc:
      raise exc

  def generate_url(self, key: str) -> str:
    return self.s3_client.generate_presigned_url(
      ClientMethod="get_object",
      Params={"Bucket": settings.S3_BUCKET_NAME, "Key": key},
      ExpiresIn=settings.S3_EXPIRES_IN
    )