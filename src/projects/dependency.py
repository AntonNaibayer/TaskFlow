from typing import Annotated
import uuid

from fastapi import Depends, HTTPException
from sqlalchemy import select

from src.auth.models import User
from src.database import SessionDep
from src.auth.dependencies import get_current_user
from src.projects.models import Project

async def get_user_project_or_404(
    project_id: uuid.UUID,
    session: SessionDep,
    current_user: Annotated[User, Depends(get_current_user)]
) -> Project:
    query = select(Project).where(
        Project.id == project_id, 
        Project.owner_id == current_user.id
    )
    result = await session.execute(query)
    project = result.scalar_one_or_none()
    
    if project is None:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    return project