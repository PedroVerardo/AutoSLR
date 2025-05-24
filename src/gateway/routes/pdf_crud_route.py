from fastapi import APIRouter, Depends 
from confluent_kafka import Producer
import json
import os
from typing import Dict, Any

from ..models import PdfQuestionModel
from ..config import get_producer, send_to_kafka
from ..config import ExtractionMethod

crud_router = APIRouter()

@crud_router.post("/ask-pdf")
async def pdf_crud(request: PdfQuestionModel):
    # topic = 'pdf_crud_topic'
    message = {
        "operation": request.operation,
        "data":{
            "question": request.data.question,
            "archive_ids": request.data.archive_ids,
            "section_title": request.data.section_title,
            "feeding_method": request.data.feeding_method,
        }
        
    }
    send_to_kafka(ExtractionMethod.CRUD, message)
    return {"status": "PDF question process triggered"}


