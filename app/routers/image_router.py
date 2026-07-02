from fastapi import APIRouter, UploadFile

from app.dependencies.permit_dependency import CurrentUserDep
from app.dependencies.image_dependency import ImageServiceDep
from app.schemas.image_schema import ImageRead

router = APIRouter()

@router.post("/upload_image", response_model=ImageRead)
async def upload_image(user: CurrentUserDep, service: ImageServiceDep, file: UploadFile):
  return await service.upload_image(user.id, file)