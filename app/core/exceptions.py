class AppBaseException(Exception):
  status_code = 500
  detail = "An error occured"

class PasswordTooShortException(AppBaseException):
  status_code = 422
  detail = "Password should have at least 8 characters"

class PasswordNoUppercaseException(AppBaseException):
  status_code = 422
  detail = "Password should have at least one big letter"

class PasswordNumberException(AppBaseException):
  status_code = 422
  detail = "Password should have at least one number"

class UsernameUnavailableException(AppBaseException):
  status_code = 409
  detail = "Username is alraedy in use"

class EmailUnavailableException(AppBaseException):
  status_code = 409
  detail = "Email is already in use"

class InvalidCredentialsException(AppBaseException):
  status_code = 401
  detail = "Incorrect username or password"

class InvalidTokenException(AppBaseException):
  status_code = 401
  detail = "Could not validate credentials"

class InactiveAccountException(AppBaseException):
  status_code = 400
  detail = "Account is inactive"

class DeletedAccountException(AppBaseException):
  status_code = 400
  detail = "Account is deleted"

class MaxFileSizeExceededException(AppBaseException):
  status_code = 413
  detail = "File size is too large"

class ImageResolutionException(AppBaseException):
  status_code = 400
  detail = "Image resolution is too large"

class InvalidImageFormatException(AppBaseException):
  status_code = 422
  detail = "Invalid image format. Allowed formats are: IMG, JPEG, WEBP"

class S3UploadFailedException(AppBaseException):
  status_code = 503
  detail = "Failed to upload image to storage"

class DuplicateImageException(AppBaseException):
  status_code = 409
  detail = "Image with the same key is already uploaded"

class ImageNotFoundException(AppBaseException):
  status_code = 404
  detail = "Image not found"