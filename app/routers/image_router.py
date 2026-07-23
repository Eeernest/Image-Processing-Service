from fastapi import APIRouter, UploadFile

from app.dependencies.permit_dependency import CurrentUserDep
from app.dependencies.image_dependency import ImageServiceDep
from app.schemas.image_schema import ImageRead

router = APIRouter()

@router.post("/upload_image", response_model=ImageRead)
async def upload_image(user: CurrentUserDep, service: ImageServiceDep, file: UploadFile):
  return await service.upload_image(user.id, file)

@router.get("/resize_image/{image_id}", response_model=ImageRead)
async def resize_image(user: CurrentUserDep, service: ImageServiceDep, image_id: int, width: int, height: int):
  return await service.resize_image(user.id, image_id, width, height)