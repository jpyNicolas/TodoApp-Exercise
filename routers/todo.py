from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

import database
from models import Todos
from database import *

router = APIRouter()
Base.metadata.create_all(bind=engine)


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(gt=0, le=5)
    is_complete: bool = Field(default=False)


@router.get("/")
async def get_todos(db: db_dependency):
    return db.query(Todos).all()


@router.get("/todos/{todo_id}")
async def get_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo is not None:
        return todo
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='not found!')


@router.post("/todos/", status_code=status.HTTP_201_CREATED)
async def create_todo(db: db_dependency, todo_request: TodoRequest):
    todo_model = Todos(**todo_request.model_dump())
    db.add(todo_model)
    db.commit()


@router.put("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model is not None:
        todo_model.title = todo_request.title
        todo_model.description = todo_request.description
        todo_model.priority = todo_request.priority
        todo_model.is_complete = todo_request.is_complete

        db.add(todo_model)
        db.commit()
        return
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='not found!')


@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db: db_dependency, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first
    if todo_model is not None:
        db.query(Todos).filter(Todos.id == todo_id).delete()
        db.commit()
