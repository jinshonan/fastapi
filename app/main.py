from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg  # this is used to connect the code with the database
# from psycopg2.extras import RealDictCursor  # has something to do with the rows?
import time
from sqlalchemy.orm import Session
from . import models, schemas  # current folder
#  from .schemas import Post  # no need for this anymore
from .database import engine, get_db


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


# while True:  # I don't see the point of keeping trying
try:
    conn = psycopg.connect(host='localhost', dbname='fastapi', user='postgres', password='1126')
    cursor = conn.cursor()
    print("database connected")
    # break
except Exception as error:
    print("Error: ", error)
    # time.sleep(2)  # sleep for 2 seconds

my_posts = []

def find_posts(id):
    for p in my_posts:
        if p['id'] == id:
            return p
        
def find_index_post(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i
    return -1

def rows_to_dict_list(cursor, rows):  
    # by default postgres doesn't output col names 
    # this is a solution
    column_names = [desc[0] for desc in cursor.description]
    return [dict(zip(column_names, row)) for row in rows]

def row_to_dict(cursor, row):
    # used when there is only one row
    if not row:  # when the post is not fonud
        return None
    column_names = [desc[0] for desc in cursor.description]
    return dict(zip(column_names, row))

# order matters and when API request is sent the below functions are checked in order

# path operation (route)
@app.get("/")  # decorator for functions
async def root():
    return {"message": "Hello"}


@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return posts


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    print(f"Received post data: {post.model_dump()}")  # Debug print
    new_post = models.Post(**post.model_dump())
    print(f"Created new post object: {vars(new_post)}")  # Debug print
    db.add(new_post)
    db.commit()
    db.refresh(new_post)  
    return new_post


@app.get("/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id).first()  # find the first instance that's a match
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"id {id} doesn't exist")
    return post

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{id} not found")
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, post: schemas.PostCreate, db: Session = Depends(get_db)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    if post_query.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"id {id} doesn't exist")
    post_query.update(post.model_dump(), synchronize_session=False)  # no idea why I don't used ** here
    db.commit()
    return post_query.first()