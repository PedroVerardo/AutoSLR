from fastapi import FastAPI
from .handlers import extraction_router
from .database import engine, Base

app = FastAPI()

app.include_router(extraction_router, prefix="/api", tags=["extraction"])

#Base.metadata.create_all(bind=engine)