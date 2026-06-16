from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.core.exceptions import AppBaseException
from app.core.exception_handler import custom_exc_handler, validation_exc_handler
from app.routers.account_router import router as account_router

app = FastAPI()

app.add_exception_handler(AppBaseException, custom_exc_handler)
app.add_exception_handler(RequestValidationError, validation_exc_handler)

app.include_router(account_router)