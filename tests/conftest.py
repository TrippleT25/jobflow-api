import os

import pytest
import pytest_asyncio
from dotenv import load_dotenv
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.database import Base, get_db
from app.main import app


load_dotenv(".env.test")

TEST_DATABASE_URL = os.environ["TEST_DATABASE_URL"]

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def override_get_db():
    async with TestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def prepare_database():
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as async_client:
        yield async_client


@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    async def fake_get_cache(key: str):
        return None

    async def fake_set_cache(
        key: str,
        value,
        expire: int = 60,
    ):
        return None

    async def fake_delete_cache_pattern(pattern: str):
        return None

    monkeypatch.setattr(
        "app.services.vacancies.get_cache",
        fake_get_cache,
    )

    monkeypatch.setattr(
        "app.services.vacancies.set_cache",
        fake_set_cache,
    )

    monkeypatch.setattr(
        "app.services.vacancies.delete_cache_pattern",
        fake_delete_cache_pattern,
    )
