import os

os.environ["S3_BUCKET_NAME"] = "test-bucket"
os.environ["SECRET_KEY"] = "test-secret-key"

os.environ["S3_ACCESS_KEY_ID"] = "testing"
os.environ["S3_SECRET_ACCESS_KEY"] = "testing"
os.environ["S3_REGION"] = "eu-north-1"

os.environ["AWS_ACCESS_KEY_ID"] = "testing"
os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
os.environ["AWS_DEFAULT_REGION"] = "eu-north-1"

import boto3
from moto import mock_aws
import pytest
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from testcontainers.postgres import PostgresContainer

from app.db.database import Base
from app.models.account_model import Account
from app.models.image_model import Image

pytest_plugins = [
  "anyio",
  "tests.fixtures.account_fixture",
  "tests.fixtures.auth_fixture",
  # "tests.fixtures.permit_fixture",
  "tests.fixtures.image_fixture",
]

@pytest.fixture(scope="session")
def anyio_backend():
  return "asyncio"

@pytest.fixture(scope="session")
def postgres_container():
  with PostgresContainer("postgres:16-alpine") as postgres:
    yield postgres

@pytest.fixture(scope="session")
def test_engine(postgres_container):
  url = postgres_container.get_connection_url().replace("postgresql+psycopg2", "postgresql+asyncpg")

  engine = create_async_engine(
    url,
    poolclass=NullPool,
  )

  return engine

@pytest.fixture(scope="session")
async def setup_database(test_engine):
  async with test_engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)

  yield 

  async with test_engine.begin() as conn:
    await conn.run_sync(Base.metadata.drop_all)
  
  await test_engine.dispose()

@pytest.fixture
async def db_session(test_engine, setup_database):
  conn = await test_engine.connect()
  trans = await conn.begin()

  test_async_session = async_sessionmaker(
    bind=conn,
    class_=AsyncSession,
    expire_on_commit=False,
    join_transaction_mode="create_savepoint"
  )

  async with test_async_session() as session:
    try:
      yield session
    finally:
      await session.close()
      await trans.rollback()
      await conn.close()

@pytest.fixture()
def mocked_aws():
  with mock_aws():
    region = "eu-north-1"
    s3 = boto3.client("s3", region_name=region)

    s3.create_bucket(Bucket=os.environ["S3_BUCKET_NAME"], CreateBucketConfiguration={"LocationConstraint": region})
    yield s3