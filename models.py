from database import Base
from sqlalchemy import Column, ForeignKey
from sqlalchemy import Integer, String, Boolean


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    hashed_passwd = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)


class Todos(Base):
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    is_complete = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('users.id'))