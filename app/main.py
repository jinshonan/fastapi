from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from fastapi.params import Body
from pydantic import BaseModel

from random import randrange
import psycopg  # this is used to connect the code with the database
import time

from . import models, schemas, utils
from .database import engine, get_db
from .routers import post, user, auth


models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)

# path operation (route)
@app.get("/")  # decorator for functions
async def root():
    return {"message": "Hello"}