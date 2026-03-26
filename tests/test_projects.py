import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_project(auth_ac: AsyncClient):
    result = await auth_ac.post(
        "/projects/",
        json={
            "title": "test_project",
            "description": "test description"
        }
    )
    assert result.status_code == 201
