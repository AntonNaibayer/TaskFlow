import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from src.database import SessionDep
from src.projects.models import Project, ProjectMember
from src.projects.dependency import get_project_or_404, AnyMember, CanManageTask, AdminOnly, OwnerOnly
from src.tasks.schemas import TaskResponse, TaskCreate, TaskUpdate
from src.tasks.models import Task
from src.tasks.dependency import get_project_task_or_404, is_project_member


task_router = APIRouter(prefix="/projects/{project_id}/tasks", tags=["Работа с задача"])


@task_router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_task(
    task_data: TaskCreate,
    session: SessionDep, 
    member: ProjectMember = Depends(CanManageTask),
    project: Project = Depends(get_project_or_404)
):   
    if task_data.assignee_id:
        await is_project_member(project_id=project.id, member_id=task_data.assignee_id, session=session)


    task_data_dct = task_data.model_dump(exclude_unset=True)

    new_task = Task(
        **task_data_dct,
        author_id = member.user_id,
        project_id = project.id
    )

    session.add(new_task)

    try:
        await session.commit()
        await session.refresh(new_task)
        return new_task
    except SQLAlchemyError:
        await session.rollback()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Не удалось создать задачу")


@task_router.get(
    "/",
    response_model = list[TaskResponse]
    )
async def get_tasks(
    session: SessionDep, 
    member: ProjectMember = Depends(AnyMember),
    project: Project = Depends(get_project_or_404)
):
    query = select(Task).join(Project).where(
        Project.id == project.id
    )

    result = await session.execute(query)
    tasks = result.scalars().all()

    return tasks


@task_router.get(
    "/{task_id}",
    response_model=TaskResponse
)
async def get_task(
    task_id: uuid.UUID,
    session: SessionDep,
    member: ProjectMember = Depends(AnyMember),
    project: Project = Depends(get_project_or_404)
):
    task = await get_project_task_or_404(
        project_id=project.id,
        task_id=task_id,
        session=session,
    )
    
    return task

@task_router.patch(
    "/{task_id}",
    response_model=TaskResponse
)
async def update_task(
    task_id: uuid.UUID,
    task_data: TaskUpdate,
    session: SessionDep,
    member: ProjectMember = Depends(CanManageTask),
    project: Project = Depends(get_project_or_404)
):
    if task_data.assignee_id:
        await is_project_member(project_id=project.id, member_id=task_data.assignee_id, session=session)
        
    task = await get_project_task_or_404(
        project_id=project.id,
        task_id=task_id,
        session=session,
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Ошибка при изменеии задачи в базе данных")


@task_router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_task(
    task_id: uuid.UUID,
    session: SessionDep,
    member: ProjectMember = Depends(AdminOnly),
    project: Project = Depends(get_project_or_404)
):
    task = await get_project_task_or_404(
        project_id=project.id,
        task_id=task_id,
        session=session,
    )

    try: 
        await session.delete(task)
        await session.commit()
    except SQLAlchemyError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Ошибка при удалении задачи из базы данных")
