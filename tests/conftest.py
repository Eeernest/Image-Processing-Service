import pytest
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from testcontainers.postgres import PostgresContainer

from app.db.database import Base

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