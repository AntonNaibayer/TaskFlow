import uuid
from datetime import datetime
from typing import List

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from projects.enums import ProjectRole
from src.database import Base

class Project(Base):
    __tablename__ = "project"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(50))
    description: Mapped[str | None] = mapped_column(String(150))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))
    members: Mapped[List["ProjectMember"]] = relationship(back_populates="project")


class ProjectMember(Base):
    __tablename__ = "project_member"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey="project.id", ondelete="CASCADE")
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey="user.id", ondelete="CASCADE")

    role: Mapped[ProjectRole] = mapped_column(default=ProjectRole.VIEWER)
    joined_at: Mapped[datetime] = mapped_column(server_default=func.now())

    project: Mapped["Project"] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="memberships")

    __table_args__ = (
        UniqueConstraint('project_id', "user_id", name="unique_project_user"),
    )