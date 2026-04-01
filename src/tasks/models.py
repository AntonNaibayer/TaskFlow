from datetime import datetime
import uuid
from typing import List

from sqlalchemy import ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.tasks.enums import TaskStatus, TaskPriority

class Task(Base):
    __tablename__ = "task"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(40))
    description: Mapped[str | None] = mapped_column(String(300))
    status: Mapped[TaskStatus] = mapped_column(default=TaskStatus.TODO)
    priority: Mapped[TaskPriority] = mapped_column(default=TaskPriority.LOW)

    project_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("project.id"))
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("user.id"))
    assignee_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("user.id"), default=None)

    # server_default — для начального значения
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    # onupdate — для каждого изменения
    update_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    project: Mapped["Project"] = relationship(back_populates="tasks")
    history: Mapped[List["TaskHistory"]] = relationship(
        back_populates="task",
        cascade="all, delete-orphan" # Если задача удалена, удалятся и его история
    )

class TaskHistory(Base):
    __tablename__ = "task_history"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('task.id'))
    change_by: Mapped[uuid.UUID] = mapped_column(ForeignKey('user.id'))
    field_name: Mapped[str] = mapped_column()
    old_value: Mapped[str] = mapped_column()
    new_value: Mapped[str] = mapped_column()
    create_at: Mapped[datetime] = mapped_column(server_default=func.now())

    task: Mapped["Task"] = relationship(back_populates="history")
    editor: Mapped["User"] = relationship()