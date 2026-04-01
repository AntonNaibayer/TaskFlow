import uuid
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict

from src.tasks.enums import TaskStatus, TaskPriority

class TaskCreate(BaseModel):
    title: str = Field(max_length=40, min_length=1)
    description: str | None = Field(max_length=300, default=None)
    status: TaskStatus = Field(default=TaskStatus.TODO)
    priority: TaskPriority = Field(default=TaskPriority.LOW)
    assignee_id: uuid.UUID | None = Field(default=None)

class TaskUpdate(BaseModel):
    title: str | None = Field(max_length=40, default=None)
    description: str | None = Field(max_length=300, default=None)
    status: TaskStatus | None = Field(default=None)
    priority: TaskPriority | None = Field(default=None)
    assignee_id: uuid.UUID | None = Field(default=None)

class TaskResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    status: TaskStatus
    priority: TaskPriority

    project_id: uuid.UUID
    author_id: uuid.UUID 
    assignee_id: uuid.UUID | None
    
    created_at: datetime
    update_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TaskFilters(BaseModel):
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    search: str | None = None


class TaskHistoryResponse(BaseModel):
    id: uuid.UUID
    task_id: uuid.UUID
    change_by: uuid.UUID
    field_name: str
    old_value: str | None
    new_value: str
    create_at: datetime