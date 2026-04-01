from typing import List
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError, IntegrityError


from src.database import SessionDep
from src.auth.dependencies import CurrentUserDep
from src.projects.models import Project, ProjectMember
from src.projects.schemas import ProjectMemberAdd, ProjectMemberResponse, ProjectResponse, ProjectCreate, ProjectUpdate
from src.projects.enums import ProjectRole
from src.projects.dependency import get_project_or_404, AnyMember, AdminOnly, OwnerOnly





project_router = APIRouter(prefix = "/projects", tags=["Работа с проектами"])


@project_router.post(
    "/", 
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_project(
    project_data: ProjectCreate, 
    session: SessionDep, 
    current_user: CurrentUserDep
):

    new_project = Project(
        title=project_data.title, 
        description=project_data.description,  
        owner_id = current_user.id
    )

    owner_member = ProjectMember(
        project_id=new_project.id,
        user_id=current_user.id,
        role=ProjectRole.OWNER
    )
    
    #Cascading Save-Update: SQLA понимаем что между объектами есть свзяь -> 
    # все связанные объкты попадают в очередь для сохранения
    new_project.members.append(owner_member)

    session.add(new_project)
    try:
        await session.commit()
        await session.refresh(new_project)

        return new_project
    
    except SQLAlchemyError:
        # Если что-то пошло не так на уровне базы, откатываем изменения!
        await session.rollback()
        # Возвращаем клиенту понятную ошибку 400 (Bad Request)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Ошибка при создании проекта")


@project_router.get(
    "/", 
    response_model=list[ProjectResponse],
)
async def get_projects(
    session: SessionDep, 
    current_user: CurrentUserDep
):
    
    query = (
        select(Project)
        .join(ProjectMember)
        .where(
            ProjectMember.user_id == current_user.id
        )
    )

    result = await session.execute(query)

    #Алхимия по умолчанию возвращает строки из базы данных в виде кортеже/
    #т.е. projects будет выглядеть так: [(<Project id=1>), (<Project id=2>)]
    #FastAPI и Pydantic не поймут этот кортеж и выдадут ошибку при попытке превратить это в JSON
    #поэтому используем .scalars()
    # result содержит Row-объекты; scalars() извлекает из них сами Project
    projects = result.scalars().all()

    return projects


@project_router.get(
    "/{project_id}", 
    response_model=ProjectResponse
)
async def get_project_details(
    # Сначала проверяем, что юзер вообще участник (любой)
    member: ProjectMember = Depends(AnyMember),
    # Затем получаем сам проект (FastAPI закеширует вызов, если ID совпадает)
    project: Project = Depends(get_project_or_404)
):  
    return project


@project_router.patch(
    "/{project_id}", 
    response_model=ProjectResponse
)
async def update_project(
    project_data: ProjectUpdate, 
    session: SessionDep, 
    member: ProjectMember = Depends(AdminOnly),
    project: Project = Depends(get_project_or_404)
    ):
    update_data = project_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(project, key, value) # Это то же самое, что project.title = "Новый", project.description = "Ого"
    
    try:
        await session.commit()
        await session.refresh(project)

        return project
    
    except SQLAlchemyError:
        # Если что-то пошло не так на уровне базы, откатываем изменения!
        await session.rollback()
        # Возвращаем клиенту понятную ошибку 400 (Bad Request)
        raise HTTPException(status_code=400, detail="Ошибка при изменении проекта в базе данных")

@project_router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_project(
    session: SessionDep, 
    member: ProjectMember = Depends(OwnerOnly),
    project: Project = Depends(get_project_or_404)
    ):    
    try:
        await session.delete(project)
        await session.commit()

        # если не указать явно status_code=204, то FastAPI вернёт 200 OK 
        # но можно использовать status_code=status.HTTP_204_NO_CONTENT 
        #return Response(status_code=status.HTTP_204_NO_CONTENT)
    except SQLAlchemyError:
        await session.rollback()
        raise HTTPException(status_code=400, detail = "Ошибка при удалении проекта из базы данных")


@project_router.post(
        "/{project_id}/members",
        response_model=ProjectMemberResponse
)
async def add_memeber(
    member_data: ProjectMemberAdd,
    session: SessionDep,
    member: ProjectMember = Depends(AdminOnly),
    project: Project = Depends(get_project_or_404)
):
    member_data_dct = member_data.model_dump(exclude_unset=True)

    new_member = ProjectMember(
        **member_data_dct,
        project_id=project.id
    )

    session.add(new_member)
    try:
        await session.commit()
        await session.refresh(new_member)

        return new_member
    except IntegrityError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail = "Пользователь уже состоит в этом проекте"
        )
    except SQLAlchemyError:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail = "Неудалось добавить пользователя"
        )
    

@project_router.get(
    "/{project_id}/members",
    response_model=List[ProjectMemberResponse]
)
async def get_project_members(
    session: SessionDep,
    member: ProjectMember = Depends(AnyMember)
):
    query = (
        select(ProjectMember)
        .where(
            ProjectMember.project_id == member.project_id
        )
    )
    result = await session.execute(query)
    return result.scalars().all()