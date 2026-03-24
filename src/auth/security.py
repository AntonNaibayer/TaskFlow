import jwt
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext

from src.config import settings

#Параметр deprecated="auto" указывает использовать рекомендованные схемы хэширования и автоматически обновлять устаревшие
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

#Функция принимает пароль в виде строки и возвращает его безопасный хэш
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


#Функция принимает обычный пароль и его хэш, возвращая True, если пароль соответствует хэшу, и False в противном случае.
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    # Делаем копию данных, чтобы случайно не изменить оригинал
    to_encode = data.copy()

    # Высчитываем время, когда токен "протухнет" (текущее время + 30 минут)
    # Используем timezone.utc, это стандарт для JWT
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    # Добавляем время истечения в наши данные под специальным ключом "exp" (expiration)
    to_encode.update({"exp": expire})

    # Генерируем сам токен! 
    # jwt.encode берет наши данные, зашифровывает их алгоритмом HS256 с помощью нашего секретного ключа
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    return encoded_jwt