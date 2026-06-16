from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from app.core.exceptions import AppBaseException

def custom_exc_handler(request: Request, exc: AppBaseException):
  headers = {}

  if exc.status_code == status.HTTP_401_UNAUTHORIZED:
    headers["WWW-Authenticate"] = "Bearer"

  return JSONResponse(
    status_code=exc.status_code,
    content={"detail": exc.detail},
    headers=headers
  )

def validation_exc_handler(request: Request, exc: RequestValidationError):
  return JSONResponse(
    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
    content={
      "detail": "Wrong input data",
      "errors": exc.errors()
    }
  )