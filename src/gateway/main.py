from fastapi import FastAPI
from .routes import pdf_extraction_router

app = FastAPI()

# Include v1 API routes
app.include_router(pdf_extraction_router, prefix="/api/v1", tags=["pdf_extraction_v1"])
