from fastapi import APIRouter
from pydantic import BaseModel, Field
import bcrypt
from models import Users

router = APIRouter()


def passwd_hashing(passwd: str):
    passwd = passwd.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(passwd, salt)


class CreateUserRequest(BaseModel):
    email: str
    username: str
    passwd: str
    is_active: bool = Field(default=True)


@router.post("/users")
async def create_user(create_user_request: CreateUserRequest):
    user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        hashed_passwd=passwd_hashing(create_user_request.passwd),
        is_active=create_user_request.is_active
    )
    return user_model
