import uuid

from alembic.util import status
from fastapi import HTTPException

from sqlalchemy import select

from projects.enums import ProjectRole
from src.database import SessionDep
from src.auth.models import User
from src.auth.dependencies import CurrentUserDep
from src.projects.models import Project, ProjectMember

async def get_project_or_404(
    project_id: uuid.UUID,
    session: SessionDep
) -> Project:
    project = await session.get(Project, project_id)

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )
    return project

class RoleChecker:
    def __init__(self, allowed_roles: list[ProjectRole]) -> None:
        self.allowed_roles = self.allowed_roles

    async def __call__(
        self,
        project_id: uuid.UUID,
        current_user: CurrentUserDep,
        session: SessionDep
    ) -> ProjectMember:
        query = (
            select(ProjectMember)
            .where(
                ProjectMember.project_id == project_id,
                ProjectMember.user_id == current_user.id
            )
        )
        result = await session.execute(query)
        member = result.scalar_one_or_none()

        if not member:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Проект не найден"
            )
        
        if member.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав для выполнения операции"
            )

        return member

AnyMember = RoleChecker([ProjectRole.OWNER, ProjectRole.ADMIN, ProjectRole.VIEWER])
AdminOnly = RoleChecker([ProjectRole.OWNER, ProjectRole.ADMIN])
OwnerOnly = RoleChecker([ProjectRole.OWNER])