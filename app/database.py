# using python package to manipulate postgres database

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQLALCHEMY_DATABASE_URL = 'postgresql://<username>:<password>@ip/<hostname>/<database_name>'
SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:1126@localhost/fastapi'

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit = False, autoflush=False, bind=engine)

Base = declarative_base()

# the "dependancy"
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()