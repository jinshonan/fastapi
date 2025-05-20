from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from random import randrange
from . import models
from .database import engine
from .routers import post, user, auth, vote
from .config import settings

# this is used to create the tables
# won't comment it out since I don't like alembic
models.Base.metadata.create_all(bind=engine)

origins = ["https://www.google.com"]  # allow this website to talk to our server

app = FastAPI()
app.add_middleware(  # this is for CORS
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
) 


app.include_router(post.router)
app.include_router(user.router)
app.include_router(auth.router)
app.include_router(vote.router)

# path operation (route)
@app.get("/")  # decorator for functions
async def root():
    return {"message": "API is running"}