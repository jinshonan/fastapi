from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, Annotated


"""-------------------------------USER RELATED CODE--------------------------------------"""


class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    class Config:
        orm_mode = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str



class TokenData(BaseModel):
    id: Optional[str] = None

"""-------------------------------POST RELATED CODE--------------------------------------"""


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):  # pass PostBase here to inherit the class
    pass


class Post(PostBase):  # make sure the response is in this format
    id: int
    created_at: datetime
    owner_id: int
    owner: UserOut

    class Config:  # convert a sql model to a pydentic one
        orm_mode = True

class PostOut(BaseModel):  # shouldn't inherit PostBase?
    Post: Post
    votes: int

    class Config:  # convert a sql model to a pydentic one
        orm_mode = True


"""-------------------------------VOTE RELATED CODE--------------------------------------"""

class Vote(BaseModel):
    post_id: int
    dir: Annotated[int, Field(le=1)]  # "direction": recommended syntax in Pydantic v2, it's 0 or 1
