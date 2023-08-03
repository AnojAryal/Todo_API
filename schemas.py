from pydantic import BaseModel
from typing import Optional, List


class TodoBase(BaseModel):
    title: str
    description: str
    completed: bool


class Todo(TodoBase):
    class Config:
        orm_mode = True


class User(BaseModel):
    name: str
    username: str
    password: str


class Show_User(BaseModel):
    name: str
    username: str
    blogs: List[Todo] = []

    class Config:
        orm_mode = True


class showTodo(BaseModel):
    title: str
    description: str
    creator: Show_User

    class Config:
        # Enable Pydantic's ORM mode
        orm_mode = True  # This allows the model to work  with ORMs


class TodoItem(BaseModel):
    id: int
    title: str
    description: str
    completed: bool


class Login(BaseModel):
    username: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
