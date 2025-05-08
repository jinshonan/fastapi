from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg  # this is used to connect the code with the database
# from psycopg2.extras import RealDictCursor  # has something to do with the rows?
import time

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
    column_names = [desc[0] for desc in cursor.description]
    return dict(zip(column_names, row))

# order matters and when API request is sent the below functions are checked in order

# path operation (route)
@app.get("/")  # decorator for functions
async def root():
    return {"message": "Hello"}

@app.get("/posts")
def get_posts():
    cursor.execute("""select * from posts""")
    results = cursor.fetchall()
    posts = rows_to_dict_list(cursor, results)
    return {"data": posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    cursor.execute("""
                   insert into posts (title, content, published) 
                   values (%s, %s, %s)
                   returning * 
                   """,
                   (post.title,
                   post.content,
                   post.published))
    result = cursor.fetchone()
    new_post = row_to_dict(cursor, result)
    conn.commit()  # the save the changes
    return {"data": new_post}

@app.get("/posts/{id}")
def get_post(id: int):
    cursor.execute("""select * from posts where id = %s """, (id,))  # funny that it requires a comma to work
    result = cursor.fetchone()
    post = row_to_dict(cursor, result)
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{id} not found")
    return {"detail": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, response: Response):
    cursor.execute("""delete from posts where id = %s returning *""", (id,))
    result = cursor.fetchone()
    deleted_post = row_to_dict(cursor, result)
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{id} not found")
    conn.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def delete_post(id: int, post: Post, response: Response):
    i = find_index_post(id)
    if i == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{id} not found")
    post_dict = post.model_dump()
    post_dict["id"] = id
    my_posts[i] = post_dict
    return {"data": post_dict}