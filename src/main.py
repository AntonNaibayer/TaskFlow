from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.database import SessionDep, Base, setup_database
from src.auth.router import auth_router
from src.projects.router import project_router
from src.tasks.router import task_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Код здесь выполнится ПЕРЕД стартом приложения
    await setup_database()
    print("База данных готова к работе")

    yield

    # Код здесь выполнится ПРИ выключении приложения
    print("Приложение завершает работу")


app = FastAPI(lifespan=lifespan)

app.include_router(project_router)
app.include_router(auth_router)
app.include_router(task_router)