import os

import pytest

from tests.fixtures.image_fixture import s3_repo, file_bytes, key

@pytest.mark.anyio
@pytest.mark.integration
async def test_upload_to_s3_success(mocked_aws, s3_repo, file_bytes, key):
  await s3_repo.upload_to_s3(file_bytes, key, "image/jpeg")
  result = mocked_aws.get_object(Bucket=os.environ["S3_BUCKET_NAME"], Key=key)

  assert result["Body"].read() == file_bytes
  assert result["ContentType"] == "image/jpeg"

@pytest.mark.anyio
@pytest.mark.integration
async def test_upload_to_s3_guess_content_type(mocked_aws, s3_repo, file_bytes):
  png_key = "uploads/test_image/image.png"

  await s3_repo.upload_to_s3(file_bytes=file_bytes, key=png_key)
  result = mocked_aws.get_object(Bucket=os.environ["S3_BUCKET_NAME"], Key=png_key)

  assert result["ContentType"] == "image/png"

@pytest.mark.anyio
@pytest.mark.integration
async def test_upload_to_s3_fallback_content_type(mocked_aws, s3_repo, file_bytes):
  unknown_key = "unknown_key"

  await s3_repo.upload_to_s3(file_bytes, unknown_key)
  result = mocked_aws.get_object(Bucket=os.environ["S3_BUCKET_NAME"], Key=unknown_key)

  assert result["ContentType"] == "image/jpeg"