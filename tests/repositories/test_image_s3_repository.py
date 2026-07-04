import os

from botocore.exceptions import ClientError
import pytest

@pytest.mark.anyio
@pytest.mark.integration
async def test_upload_to_s3_success(mocked_aws, image_s3_repo, file_bytes, key):
  await image_s3_repo.upload_to_s3(file_bytes, key, "image/jpeg")
  result = mocked_aws.get_object(Bucket=os.environ["S3_BUCKET_NAME"], Key=key)

  assert result["ContentType"] == "image/jpeg"

@pytest.mark.anyio
@pytest.mark.integration
async def test_delete_from_s3(mocked_aws, image_s3_repo, file_bytes, key):
  await image_s3_repo.upload_to_s3(file_bytes, key, "image/jpeg")

  result = await image_s3_repo.delete_from_s3(key)

  with pytest.raises(ClientError) as exc:
        mocked_aws.get_object(Bucket=os.environ["S3_BUCKET_NAME"], Key=key)
        
  assert result == {"message": "Image deleted"}
  assert exc.value.response["Error"]["Code"] == "NoSuchKey"

@pytest.mark.anyio
@pytest.mark.integration
async def test_download_from_s3(image_s3_repo, file_bytes, key):
   await image_s3_repo.upload_to_s3(file_bytes, key, "image/jpeg")

   result = await image_s3_repo.download_from_s3(key)

   assert result == file_bytes