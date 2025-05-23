from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
#from sqlalchemy_timescaledb import 
from sqlalchemy.sql import text
import os

DATABASE_URL = os.getenv("DATABASE_URL", "timescaledb://postgres:postgres@localhost:5432/article_search")

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector CASCADE;"))
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vectorscale CASCADE;"))
    conn.commit()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    return db