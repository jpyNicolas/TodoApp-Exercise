from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from models import Todos
from database import *
from .auth import get_current_user

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)
current_user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get("/todo", status_code=status.HTTP_200_OK)
async def get_all_todo(user: current_user_dependency, db: db_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication failed!')
    return db.query(Todos).all()
