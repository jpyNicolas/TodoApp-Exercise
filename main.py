from fastapi import FastAPI

from database import Base, engine
from routers import todo, auth, admin
app = FastAPI()
Base.metadata.create_all(bind=engine)
app.include_router(todo.router)
app.include_router(auth.router)
app.include_router(admin.router)