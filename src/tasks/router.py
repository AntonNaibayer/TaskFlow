import uuid

from fastapi import APIRouter,  HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from src.database import SessionDep
from src.auth.dependencies import CurrentUserDep
from src.projects.models import Project
from src.projects.dependency import get_user_project_or_404
from src.tasks.schemas import TaskResponse, TaskCreate, TaskUpdate
from src.tasks.models import Task
from src.tasks.dependency import get_project_task_or_404


task_router = APIRouter(prefix="/tasks", tags=["Работа с задача"])


@task_router.get(
    "/",
    response_model = list[TaskResponse]
    )
async def get_tasks(
    project_id: uuid.UUID,
    session: SessionDep, 
    current_user: CurrentUserDep
):
    query = select(Task).join(Project).where(
        Project.id == project_id,
        Project.owner_id == current_user.id
    )

    result = await session.execute(query)
    tasks = result.scalars().all()

    return tasks


@task_router.post(
    "/",
    response_model=TaskResponse,
)
async def create_task(
    task_data: TaskCreate,
    project_id: uuid.UUID,
    session: SessionDep, 
    current_user: CurrentUserDep
):
    await get_user_project_or_404(project_id=project_id, session=session, current_user=current_user)
    
    new_task = Task(
        title = task_data.title,
        description = task_data.description,
        status = task_data.status,
        project_id = project_id,
        author_id = current_user.id,
        assignee_id = task_data.assignee_id
    )

    session.add(new_task)

    try:
        await session.commit()
        await session.refresh(new_task)
        return new_task
    except SQLAlchemyError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Ошибка при сохранении задачи в базу данных")

@task_router.get(
    "/{task_id}",
    response_model=TaskResponse
)
async def get_task(
    task_id: uuid.UUID,
    project_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUserDep
):
    task = await get_project_task_or_404(
        project_id=project_id,
        task_id=task_id,
        session=session,
        current_user=current_user
    )
    
    return task

@task_router.patch(
    "/{task_id}",
    response_model=TaskResponse
)
async def update_task(
    task_id: uuid.UUID,
    task_data: TaskUpdate,
    project_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUserDep,
):
    task = await get_project_task_or_404(
        project_id=project_id,
        task_id=task_id,
        session=session,
        current_user=current_user
    )
    
    update_data = task_data.model_dump(exclude_unset=True)

    for key, val in update_data.items():
        setattr(task, key, val)
    
    try:
        await session.commit()
        await session.refresh(task)
        return task
    except SQLAlchemyError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Ошибка при изменеии задачи в базе данных")


@task_router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_task(
    task_id: uuid.UUID,
    project_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUserDep
):
    task = await get_project_task_or_404(
        project_id=project_id,
        task_id=task_id,
        session=session,
        current_user=current_user
    )

    try: 
        await session.delete(task)
        await session.commit()
    except SQLAlchemyError:
        await session.rollback()
        raise HTTPException(status_code=400, detail="Ошибка при удалении задачи из базы данных")
