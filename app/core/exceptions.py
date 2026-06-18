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