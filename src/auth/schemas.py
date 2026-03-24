
import uuid

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8) # запрещаем слишком короткие пароли
    username: str = Field(max_length=30) # запрещаем слишком длинные ники

class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    username: str

    # Эта строчка говорит Pydantic: "Не ругайся, что тебе дают объект SQLAlchemy, 
    # просто вытащи из него нужные атрибуты"
    model_config = ConfigDict(from_attributes=True)