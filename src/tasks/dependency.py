import uuid


from sqlalchemy import select
from fastapi import HTTPException, status

from src.database import SessionDep
from src.projects.models import Project, ProjectMember
from src.tasks.models import Task

async def get_project_task_or_404(
        project_id: uuid.UUID,
        task_id: uuid.UUID,
        session: SessionDep
):
    query = select(Task).join(Project).where(
        Project.id == project_id,
        Task.id == task_id,
    )

    result = await session.execute(query)
    task = result.scalar_one_or_none()

    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Задача не найдена или у вас нет доступа"
        )
    
    return task


async def is_project_member(
    project_id: uuid.UUID,
    member_id: uuid.UUID,
    session: SessionDep
):
    query = (
        select(ProjectMember)
        .where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == member_id
        )
    )

    result = await session.execute(query)
    member = result.scalar_one_or_none()

    if not member:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь не состоит в проекте"
        )
    
    return member

    