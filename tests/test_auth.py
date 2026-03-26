import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_register_user(ac: AsyncClient):
    response = await ac.post(
        "/users/register",
        json={
            "email": "anton@gmail.com",
            "password": "qwerty123",
            "username": "Kritplay"
        }
    )
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_login_user(ac: AsyncClient):
    response = await ac.post(
        "/users/login",
        data={
            "username": "anton@gmail.com",
            "password": "qwerty123"
        }
    )
    assert response.status_code == 200