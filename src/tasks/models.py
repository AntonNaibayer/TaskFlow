import uuid
from enum import Enum
from sqlalchemy import ForeignKey, String, null
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class TaskStatus(Enum):
    TODO = 'To-Do'
    PROGRESS = 'In Progress'
    DONE = "Done"

    
class Task(Base):
    __tablename__ = "task"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(40))
    description: Mapped[str | None] = mapped_column(String(300))
    status: Mapped[TaskStatus] = mapped_column(default=TaskStatus.TODO)
    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("project.id"))
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))
    assignee_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("user.id"), default=null)