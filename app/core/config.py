from pydantic_settings import BaseSettings, SettingsConfigDict

class Config(BaseSettings):
  POSTGRES_URL: str

  ADMIN_USERNAME: str = "admin_username"

  ADMIN_EMAIL: str = "admin_email"

  ADMIN_HASHED_PASSWORD: str = "admin_hashed_password"

  DUMMY_HASH: str = "dummy_hash"

  SECRET_KEY: str = "secret_key"

  ALGORITHM: str = "algorithm"

  ACCESS_TOKEN_EXPIRE_MINUTES: int = 0

  S3_BUCKET_NAME: str = "s3_bucket_name"

  S3_BUCKET_REGION: str = "s3_bucket_region"

  S3_ACCESS_KEY_ID: str = "s3_access_key"

  S3_SECRET_ACCESS_KEY: str = "s3-secret_access_key"

  model_config = SettingsConfigDict(
    env_file=".env",
    extra="ignore",
    case_sensitive=True
  )

settings = Config()