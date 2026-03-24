from datetime import datetime
import uuid

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, func

from src.database import Base

class User(Base):
    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)#генерацию UUID по умолчанию
    email: Mapped[str] = mapped_column(unique=True, index=True)#индекс для быстрого поиска
    hashed_password: Mapped[str] = mapped_column()
    username: Mapped[str] = mapped_column(String(30), unique=True)
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())#заставляем БД саму ставить время при создании
    is_active: Mapped[bool] = mapped_column(default=True)