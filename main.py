from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange

app = FastAPI()

class Post(BaseModel):
    title: str
    content: str
    published: bool = True
    rating: Optional[int] = None

my_posts = []

def find_posts(id):
    for p in my_posts:
        if p['id'] == id:
            return p

# order matters and when API request is sent the below functions are checked in order

# path operation (route)
@app.get("/")  # decorator for functions
async def root():
    return {"message": "Hello"}

@app.get("/posts")
def get_posts():
    return {"data": my_posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    post_dict = post.model_dump()
    post_dict['id'] = randrange(0, 1000000000)
    my_posts.append(post_dict)  # dict() is no longer used
    return {"data": post_dict}

@app.get("/posts/{id}")
def get_post(id: int, response: Response):
    post = find_posts(id)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{id} not found")
        # exchanged with the one liner
        # response.status_code = status.HTTP_404_NOT_FOUND
        # return {"message": f"{id} not found"}
    return {"detail": post}