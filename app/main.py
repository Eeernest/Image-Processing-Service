from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError

from app.core.exceptions import AppBaseException
from app.core.exception_handler import custom_exc_handler, validation_exc_handler

app = FastAPI()

app.add_exception_handler(AppBaseException, custom_exc_handler)
app.add_exception_handler(RequestValidationError, validation_exc_handler)