from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException, Depends
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg  # this is used to connect the code with the database
# from psycopg2.extras import RealDictCursor  # has something to do with the rows?
import time
from sqlalchemy.orm import Session
from . import models  # current folder
from .database import engine, get_db


models.Base.metadata.create_all(bind=engine)

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    published: bool = True

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


# (test)sqlalchemy version of getting all the posts
@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):
    posts = db.query(models.Post).all()
    return {"data": posts}


@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    # legacy code commented out
    # cursor.execute("""select * from posts""")
    # results = cursor.fetchall()
    # posts = rows_to_dict_list(cursor, results)
    posts = db.query(models.Post).all()
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post, db: Session = Depends(get_db)):
    # legacy code commented out
    # cursor.execute("""
    #                insert into posts (title, content, published) 
    #                values (%s, %s, %s)
    #                returning * 
    #                """,
    #                (post.title,
    #                post.content,
    #                post.published))
    # result = cursor.fetchone()
    # new_post = row_to_dict(cursor, result)
    # conn.commit()  # the save the changes
    new_post = models.Post(**post.model_dump())
    # new_post = models.Post(title=post.title, content=post.content, published=post.published)
    db.add(new_post)
    db.commit()
    db.refresh(new_post)  # retrieve the data to the variable?
    return {"data": new_post}


@app.get("/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db)):
    # legacy code commented out
    # cursor.execute("""select * from posts where id = %s """, (id,))  # funny that it requires a comma to work
    # result = cursor.fetchone()
    # post = row_to_dict(cursor, result)
    post = db.query(models.Post).filter(models.Post.id == id).first()  # find the first instance that's a match
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"id {id} doesn't exist")
    return {"detail": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    # Legacy code commented out
    # cursor.execute("""delete from posts where id = %s returning *""", (id,))
    # result = cursor.fetchone()
    # deleted_post = row_to_dict(cursor, result)
    # conn.commit()

    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{id} not found")
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def delete_post(id: int, post: Post, db: Session = Depends(get_db)):
    # legacy code commented out
    # cursor.execute("""
    #                update posts 
    #                set title = %s, content = %s, published = %s 
    #                where id = %s
    #                returning *
    #                """,
    #                (post.title,
    #                 post.content,
    #                 post.published,
    #                 id))
    # result = cursor.fetchone()
    # updated_post = row_to_dict(cursor, result)
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    if post_query.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"id {id} doesn't exist")
    post_query.update(post.model_dump(), synchronize_session=False)  # no idea why I don't used ** here
    db.commit()
    return {"status": post_query.first()}