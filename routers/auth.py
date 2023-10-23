from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import bcrypt
from starlette import status

from models import Users
from database import db_dependency
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


def passwd_hashing(passwd: str):
    passwd = passwd.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(passwd, salt)


def authenticate_user(db: db_dependency, username: str, password: str):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt.checkpw(password.encode('utf-8'), user.hashed_passwd):
        return False
    return True


class CreateUserRequest(BaseModel):
    email: str
    username: str
    passwd: str
    is_active: bool = Field(default=True)


@router.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        hashed_passwd=passwd_hashing(create_user_request.passwd),
        is_active=create_user_request.is_active
    )

    db.add(user_model)
    db.commit()


@router.post("/token")
async def get_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return 'failed authentication'
    return 'successful authentication'
