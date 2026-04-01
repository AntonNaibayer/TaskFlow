import uuid
from datetime import datetime
from typing import List

from pydantic import BaseModel, Field, ConfigDict

from src.projects.enums import ProjectRole


class ProjectMemberAdd(BaseModel):
    user_id: uuid.UUID
    role: ProjectRole

class ProjectMemberUpdate(BaseModel):
    role: ProjectRole

class ProjectMemberResponse(BaseModel):
    user_id: uuid.UUID
    role: ProjectRole
    joined_at: datetime


class ProjectCreate(BaseModel):
    title: str = Field(max_length=50)
    description: str | None = Field(max_length=150)

class ProjectUpdate(BaseModel):
    title: str | None = Field(max_length=50, default=None)
    description: str | None = Field(max_length=150, default=None)

class ProjectResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    owner_id: uuid.UUID
    members: List[ProjectMemberResponse]

    model_config = ConfigDict(from_attributes=True)    