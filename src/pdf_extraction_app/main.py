from fastapi import FastAPI
from .handlers import extraction_router

app = FastAPI()

app.include_router(extraction_router, prefix="/api", tags=["extraction"])
