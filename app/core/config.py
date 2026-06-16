from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
  POSTGRES_URL: str

  ADMIN_USERNAME: str

  ADMIN_EMAIL: str

  ADMIN_HASHED_PASSWORD: str

  model_config = SettingsConfigDict(
    env_file=".env",
    extra="ignore",
    case_sensitive=True
  )

settings = Config()