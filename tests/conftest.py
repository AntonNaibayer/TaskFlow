import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from src.main import app
from src.database import get_session, Base

# URL тестовой базы
TEST_DATABASE_URL = "postgresql+asyncpg://postgres:fy2896@127.0.0.1:5432/test_taskflow_db"

# создаем независимый движок специально для тестов
test_engine = create_async_engine(TEST_DATABASE_URL)
test_session_maker = async_sessionmaker(test_engine, expire_on_commit=False)

#  функция, которая заменит оригинальный get_session
async def override_get_session():
    async with test_session_maker() as session:
        yield session

# ГЛАВНАЯ МАГИЯ FASTAPI: подменяем зависимость!
app.dependency_overrides[get_session] = override_get_session

# Фикстура для подготовки тестовой базы (сработает 1 раз перед тестами)
@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_test_db():
    async with test_engine.begin() as conn:
        # В тестовой базе мы МОЖЕМ себе позволить удалять всё перед тестами
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    

@pytest_asyncio.fixture(scope="session")
async def ac():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest_asyncio.fixture(scope="session")
async def auth_ac(ac: AsyncClient):
    await ac.post(
        "/users/register",
        json={
            "email": "test@gmail.com",
            "password": "test1234",
            "username": "TEST"
        }
    )

    login_response = await ac.post(
        "/users/login",
        data={
            "username": "test@gmail.com",
            "password": "test1234"
        }
    )
    #получаем аксес токен
    token = login_response.json()["access_token"]

    #передаём аксес токен
    ac.headers["Authorization"] = f"Bearer {token}"

    yield ac