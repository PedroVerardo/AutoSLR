from fastapi import FastAPI
from routes import pdf_operation_router

app = FastAPI()

app.include_router(pdf_operation_router, prefix="/pdf_database", tags=["pdf_extraction"])
