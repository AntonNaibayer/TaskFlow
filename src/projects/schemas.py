import uuid

from pydantic import BaseModel, Field, ConfigDict

class ProjectCreate(BaseModel):
    title: str = Field(max_length=50)
    description: str | None = Field(max_length=150)

class ProjectUpdate(BaseModel):
    title: str = Field(max_length=50)
    description: str | None = Field(max_length=150, default=None)
    
class ProjectResponse(BaseModel):
    id: uuid.UUID
    title: str
    description: str | None
    owner_id: uuid.UUID

    model_config = ConfigDict(from_attributes=True)