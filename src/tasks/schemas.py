import uuid

from pydantic import BaseModel, Field, ConfigDict
from src.tasks.models import TaskStatus

class TaskCreate(BaseModel):
    title: str = Field(max_length=40, min_length=1)
    description: str | None = Field(max_length=300, default=None)
    status: TaskStatus = Field(default=TaskStatus.TODO)
    assignee_id: uuid.UUID | None = Field(default=None)

class TaskUpdate(BaseModel):
    title: str | None = Field(max_length=40, default=None)
    description: str | None = Field(max_length=300, default=None)
    status: TaskStatus | None = Field(default=None)
    assignee_id: uuid.UUID | None = Field(default=None)

class TaskResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    status: TaskStatus
    project_id: uuid.UUID
    author_id: uuid.UUID 
    assignee_id: uuid.UUID | None

    model_config = ConfigDict(from_attributes=True)