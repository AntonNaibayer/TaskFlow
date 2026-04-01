from pydantic import BaseModel, Field, ConfigDict

class PaginationParams(BaseModel):
    limit: int = Field(default=10, ge=1, le=100, description="Количество записей")
    offset: int = Field(default=0, ge=0, description="Смещение от начала")

    model_config = ConfigDict(extra="forbid")

