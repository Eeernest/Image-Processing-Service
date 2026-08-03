from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.dependencies.auth_dependency import AuthServiceDep
from app.schemas.token_schema import TokenRead, RefreshTokenRequest

router = APIRouter()

@router.post("/token", response_model=TokenRead)
async def login(service: AuthServiceDep, data: OAuth2PasswordRequestForm = Depends()):
  return await service.login(data.username, data.password)

@router.post("/refresh_token", response_model=TokenRead)
async def refresh_token(service: AuthServiceDep, encoded_refresh_token: RefreshTokenRequest):
  return await service.refresh_token(encoded_refresh_token)