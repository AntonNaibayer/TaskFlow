import uuid

from sqlalchemy import select
from fastapi import HTTPException

from src.database import SessionDep
from src.auth.dependencies import CurrentUserDep
from src.projects.models import Project
from src.tasks.models import Task

async def get_project_task_or_404(
        project_id: uuid.UUID,
        task_id: uuid.UUID,
        session: SessionDep,
        current_user: CurrentUserDep
):
    query = select(Task).join(Project).where(
        Project.id == project_id,
        Task.id == task_id,
        Project.owner_id == current_user.id
    )

    result = await session.execute(query)
    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(status_code=404, detail="Задача не найдена или у вас нет доступа")
    
    return task
