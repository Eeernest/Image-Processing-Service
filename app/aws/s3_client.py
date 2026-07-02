from typing import Annotated

import boto3
from fastapi import Depends
from types_boto3_s3 import S3Client

from app.core.config import settings

def s3_client():
  return boto3.client(
      "s3",
      region_name=settings.S3_BUCKET_REGION,
      aws_access_key_id=(
          settings.S3_ACCESS_KEY_ID
      ),
      aws_secret_access_key=(
          settings.S3_SECRET_ACCESS_KEY
      ),
      endpoint_url=settings.S3_ENDPOINT_URL
  )

def get_s3_client():
  client = s3_client()

  yield client

S3ClientDep = Annotated[S3Client, Depends(get_s3_client)]