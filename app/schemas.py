from pydantic import BaseModel
from datetime import datetime


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(PostBase):  # pass PostBase here to inherit the class
    pass


class Post(PostBase):  # make sure the response is in this format
    id: int
    created_at: datetime

    class Config:
        # For Pydantic V1
        orm_mode = True
        # For Pydantic V2
        # from_attributes = True