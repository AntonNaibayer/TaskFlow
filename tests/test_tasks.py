import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_task(auth_ac: AsyncClient):
    project_response = await auth_ac.post(
        "/projects/",
        json={
            "title": "test_project_create_task",
            "description": "test description"
        }
    )
    project_id = project_response.json()["id"]

    result = await auth_ac.post(
        f"/projects/{project_id}/tasks/",
        json={
            "title": "task1",
            "description": "desc",
        }
    )

    assert result.status_code == 201, result.json()