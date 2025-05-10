from pydantic import BaseModel


class PostBase(BaseModel):
    title: str
    content: str
    published: bool = True


class PostCreate(BaseModel):
    pass


class Post(BaseModel):  # make sure the response is in this format somehow
    title: str
    content: str
    published: bool

    class Config:
        # For Pydantic V1
        orm_mode = True
        # For Pydantic V2
        from_attributes = True