from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
  POSTGRES_URL: str

  model_config = SettingsConfigDict(
    env_file=".env",
    extra=False,
    case_sensitive=True
  )

settings = Config()