from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
import jwt

from src.database import SessionDep
from src.config import settings
from src.auth.models import User


# Указываем URL, по которому Swagger будет ходить за токеном.
# Важно: здесь пишем путь к твоему эндпоинту логина (без первого слеша)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/login")

async def get_current_user(session: SessionDep, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, key=settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        #algorithms - ожидает получить список разрешенных алгоритмов, даже если алгоритм всего один
        user_id = payload["sub"]

        query = select(User).where(User.id == user_id)

        result = await session.execute(query)
        existing_user = result.scalar_one_or_none()

        if not existing_user:
            raise HTTPException(status_code = 401, detail = "Ошибка в доступе")
        return existing_user
    
    except (KeyError, jwt.ExpiredSignatureError, jwt.PyJWTError):
        
        raise HTTPException(status_code=401, detail="Ошибка доступа")
    

CurrentUserDep = Annotated[User, Depends(get_current_user)]