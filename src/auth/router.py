from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import select, or_
from fastapi.security import OAuth2PasswordRequestForm

from src.auth.models import User
from src.auth.schemas import UserCreate, UserResponse
from src.auth.security import get_password_hash, verify_password, create_access_token
from src.database import SessionDep
from src.auth.dependencies import get_current_user

auth_router = APIRouter(prefix='/users', tags=['Работа с пользователями'])

@auth_router.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, session: SessionDep):
    # так как у нас email и username могут быть только уникальными, проверяем нету ли совпадений
    query = select(User).where(or_(
        User.email == user_data.email, 
        User.username == user_data.username)
    )
    
    result = await session.execute(query)
    existing_user = result.scalar_one_or_none()

    #проверяем есть ли что-то в ответе
    if existing_user:
        raise HTTPException(status_code=409, detail="Пользователь с такой почтой уже зарегистрирован!")
    
    hash_password = get_password_hash(user_data.password)

    new_user = User(email = user_data.email, hashed_password = hash_password, username = user_data.username)


    session.add(new_user)

    await session.commit()

    # Обновляем объект, чтобы подтянуть все данные из БД (например, сгенерированный ID, если бы он генерировался базой)
    await session.refresh(new_user)


    # Просто возвращаем объект Алхимии! Магия FastAPI и from_attributes=True сделают остальное.
    return new_user


#В FastAPI есть удобный стандарт: если мы хотим, чтобы в Swagger заработала зеленая кнопка "Authorize", нам нужно принимать данные не через обычную Pydantic-схему, а через специальный класс OAuth2PasswordRequestForm.
@auth_router.post("/login")
async def login_user(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], session: SessionDep):
    #OAuth2PasswordRequestForm устроенна так что даже если ты логинешься с помощью почты она отдаст тебе объект с атрибутом username
    query = select(User).where(User.email == form_data.username)

    result = await session.execute(query)
    existing_user = result.scalar_one_or_none()

    if not existing_user:
        raise HTTPException(status_code = 401, detail = "Неверный email или пароль")

    if not verify_password(form_data.password, existing_user.hashed_password):
        raise HTTPException(status_code=401, detail="Неверный email или пароль" )

    access_token = create_access_token(data={"sub": str(existing_user.id)})

    #ВАЖНО: Возвращаешь словарь строго такого формата (этого требует стандарт):
    return {"access_token": access_token, "token_type": "bearer"}


@auth_router.get("/me", response_model=UserResponse)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    #Слово Depends это зависимости. FastAPI говорит: "Так, стоп. Я не могу запустить эндпоинт, пока не выполню эту зависимость", т.е. сначала выполняем get_current_user 
    return current_user