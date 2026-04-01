from fastapi import FastAPI

from src.database import SessionDep, Base, setup_database
from src.auth.router import auth_router
from src.projects.router import project_router
from src.tasks.router import task_router



app = FastAPI()

app.include_router(project_router)
app.include_router(auth_router)
app.include_router(task_router)