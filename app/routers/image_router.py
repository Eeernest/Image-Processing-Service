from fastapi import APIRouter, UploadFile

from app.dependencies.permit_dependency import CurrentUserDep
from app.dependencies.image_dependency import ImageServiceDep
from app.schemas.image_schema import ImageRead, ImageFormat

router = APIRouter()

@router.post("/upload_image", response_model=ImageRead)
async def upload_image(user: CurrentUserDep, service: ImageServiceDep, file: UploadFile):
  return await service.upload_image(user.id, file)

@router.get("/resize_image/{image_id}", response_model=ImageRead)
async def resize_image(user: CurrentUserDep, service: ImageServiceDep, image_id: int, width: int, height: int):
  return await service.resize_image(user.id, image_id, width, height)

@router.get("/crop_center_image/{image_id}", response_model=ImageRead)
async def crop_center_image(user: CurrentUserDep, service: ImageServiceDep, image_id: int, width: int, height: int):
  return await service.crop_center_image(user.id, image_id, width, height)

@router.get("/change_image_format/{image_id}", response_model=ImageRead)
async def change_image_format(user: CurrentUserDep, service: ImageServiceDep, image_id: int, format: ImageFormat):
  return await service.change_image_format(user.id, image_id, format)