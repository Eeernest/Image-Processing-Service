import os

import pytest

from tests.fixtures.image_fixture import s3_repo, file_bytes, key

@pytest.mark.integration
def test_upload_to_s3_success(mocked_aws, s3_repo, file_bytes, key):
  result = s3_repo.upload_to_s3(file_bytes, key, "image/jpeg")
  s3_object = mocked_aws.get_object(Bucket=os.environ["S3_BUCKET_NAME"], Key=key)

  assert result == key
  assert s3_object["Body"].read() == file_bytes
  assert s3_object["ContentType"] == "image/jpeg"

@pytest.mark.integration
def test_upload_to_s3_guess_content_type(mocked_aws, s3_repo, file_bytes):
  png_key = "uploads/test_image/image.png"

  result = s3_repo.upload_to_s3(file_bytes=file_bytes, key=png_key)
  s3_object = mocked_aws.get_object(Bucket=os.environ["S3_BUCKET_NAME"], Key=png_key)

  assert result == png_key
  assert s3_object["ContentType"] == "image/png"

@pytest.mark.integration
def test_upload_to_s3_fallback_content_type(mocked_aws, s3_repo, file_bytes):
  unknown_key = "unknown_key"

  result = s3_repo.upload_to_s3(file_bytes, unknown_key)
  s3_object = mocked_aws.get_object(Bucket=os.environ["S3_BUCKET_NAME"], Key=unknown_key)

  assert result == unknown_key
  assert s3_object["ContentType"] == "image/jpeg"