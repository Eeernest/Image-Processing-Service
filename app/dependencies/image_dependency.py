from typing import Annotated

from fastapi import Depends

from app.aws.s3_client import S3ClientDep
from app.db.database import SessionDep
from app.repositories.image_db_repository import ImageDbRepository
from app.repositories.image_s3_repository import ImageS3Repository
from app.services.image_service import ImageService

def get_image_service(session: SessionDep, client: S3ClientDep):
  db_repo = ImageDbRepository(session)
  s3_repo = ImageS3Repository(client)

  return ImageService(db_repo, s3_repo)

ImageServiceDep = Annotated[ImageService, Depends(get_image_service)]