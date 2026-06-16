from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
  POSTGRES_URL: str

  ADMIN_USERNAME: str = "admin_username"

  ADMIN_EMAIL: str = "admin_email"

  ADMIN_HASHED_PASSWORD: str = "admin_hashed_password"

  model_config = SettingsConfigDict(
    env_file=".env",
    extra="ignore",
    case_sensitive=True
  )

settings = Config()