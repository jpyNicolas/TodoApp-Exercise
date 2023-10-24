from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
import bcrypt
from starlette import status

from models import Users
from database import db_dependency
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import timedelta, datetime

router = APIRouter()

SECRET_KEY = 'd462a14ccf55e670f7edc960d38304d01b1ed624f81e124ead1d80ef8435a938'
ALGORITHM = 'HS256'


class CreateUserRequest(BaseModel):
    email: str
    username: str
    passwd: str
    is_active: bool = Field(default=True)


class Token(BaseModel):
    access_token: str
    token_type: str


oauth2_bearer = OAuth2PasswordBearer(tokenUrl='token')


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
    return user


def create_access_token(username: str, user_id: int, expires_delta: timedelta):
    encode = {
        'sub': username,
        'id': user_id
    }
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: str = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='could not validate user')
        return {'username': username, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='could not validate user')


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


@router.post("/token", response_model=Token)
async def get_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        return 'failed authentication'
    token = create_access_token(user.username, user.id, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}
