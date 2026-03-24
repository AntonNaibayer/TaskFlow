import uuid

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from src.database import SessionDep
from src.projects.models import Project
from src.projects.schemas import ProjectResponse, ProjectCreate, ProjectUpdate
from src.auth.dependencies import CurrentUserDep
from src.projects.dependency import get_user_project_or_404



project_router = APIRouter(prefix = "/projects", tags=["Работа с проектами"])


@project_router.get(
    "/", 
    response_model=list[ProjectResponse],
)
async def get_projects(
    session: SessionDep, 
    current_user: CurrentUserDep
):
    
    query = select(Project).where(
        Project.owner_id == current_user.id
    )

    result = await session.execute(query)

    #Алхимия по умолчанию возвращает строки из базы данных в виде кортеже/
    #т.е. projects будет выглядеть так: [(<Project id=1>), (<Project id=2>)]
    #FastAPI и Pydantic не поймут этот кортеж и выдадут ошибку при попытке превратить это в JSON
    #поэтому используем .scalars()
    # result содержит Row-объекты; scalars() извлекает из них сами Project
    projects = result.scalars().all()

    return projects


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

    session.add(new_project)
    try:
        await session.commit()
        await session.refresh(new_project)

        return new_project
    except SQLAlchemyError:
        # Если что-то пошло не так на уровне базы, откатываем изменения!
        await session.rollback()
        # Возвращаем клиенту понятную ошибку 400 (Bad Request)
        raise HTTPException(status_code=400, detail="Ошибка при сохранении проекта в базу данных")
    

@project_router.get(
    "/{project_id}", 
    response_model=ProjectResponse
)
async def get_project(
    project_id: uuid.UUID, 
    session: SessionDep, 
    current_user: CurrentUserDep
):
    project = await get_user_project_or_404(project_id=project_id, session=session, current_user=current_user)
    return project


@project_router.patch(
    "/{project_id}", 
    response_model=ProjectResponse
)
async def update_project(
    project_id: uuid.UUID, 
    project_data: ProjectUpdate, 
    session: SessionDep, 
    current_user: CurrentUserDep
    ):

    project = await get_user_project_or_404(project_id=project_id, session=session, current_user=current_user)
    
    # project.title = project_data.title
    # project.description = project_data.description
    # а что если таких полей 20? код становится не читаемый. лучше сделать перебор

    #Превращаем данные от юзера в словарь
    # exclude_unset=True означает: "возьми только те поля, которые юзер реально прислал"
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
    project_id: uuid.UUID, 
    session: SessionDep, 
    current_user: CurrentUserDep
    ):
    project = await get_user_project_or_404(project_id=project_id, session=session, current_user=current_user)
    
    try:
        await session.delete(project)
        await session.commit()

        # если не указать явно status_code=204, то FastAPI вернёт 200 OK 
        # но можно использовать status_code=status.HTTP_204_NO_CONTENT 
        #return Response(status_code=status.HTTP_204_NO_CONTENT)
    except SQLAlchemyError:
        await session.rollback()
        raise HTTPException(status_code=400, detail = "Ошибка при удалении проекта из базы данных")
