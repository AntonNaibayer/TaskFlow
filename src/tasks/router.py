from typing import Annotated, List
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from src.common.dependency import PaginationParams
from src.database import SessionDep
from src.projects.models import Project, ProjectMember
from src.projects.dependency import get_project_or_404, AnyMember, CanManageTask, AdminOnly, OwnerOnly
from src.tasks.schemas import TaskResponse, TaskCreate, TaskUpdate, TaskFilters, TaskHistoryResponse
from src.tasks.models import Task, TaskHistory
from src.tasks.dependency import get_project_task_or_404, is_project_member
from src.tasks.constants import tracked_fields

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
    pagination: Annotated[PaginationParams, Depends()],
    filters: Annotated[TaskFilters, Query()],
    member: ProjectMember = Depends(AnyMember),
):
    query = (
        select(Task)
        .join(Project)
        .where(Project.id == member.project_id)
    )

    if filters.status:
        query = query.where(
            Task.status == filters.status
        )
    
    if filters.priority:
        query = query.where(
            Task.priority == filters.priority,
        )

    if filters.search:
        query = query.where(
            Task.title.ilike(f"%{filters.search}%")
        )

    query = (
        query
        .limit(pagination.limit)
        .offset(pagination.offset)
        .order_by(Task.created_at.desc())
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
        old_val = getattr(task, key)
        if key in tracked_fields and old_val != val:
            el = TaskHistory(
                task_id=task_id,
                change_by=member.user_id,
                field_name=str(key),
                old_value=str(old_val.value if hasattr(old_val, 'value') else old_val),
                new_value=str(val)
            )
            session.add(el)
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

@task_router.get(
    "/{task_id}/history",
    response_model=List[TaskHistoryResponse]
)
async def get_task_history(
    task_id: uuid.UUID,
    session: SessionDep,
    member: ProjectMember = Depends(AnyMember),
    project: Project = Depends(get_project_or_404)
):
    await get_project_task_or_404(
        project_id=project.id,
        task_id=task_id,
        session=session,
    )

    query = (
        select(TaskHistory)
        .where(
            TaskHistory.task_id == task_id
        )
        .order_by(TaskHistory.create_at.desc())
    )
    result = await session.execute(query)
    task_histories = result.scalars().all()

    return task_histories
