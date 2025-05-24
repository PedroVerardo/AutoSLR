from fastapi import APIRouter, Depends 
from confluent_kafka import Producer
import json
import os
from typing import Dict, Any

from ..config import get_producer, send_to_kafka
from ..models import PdfRequestModel
from ..config import ExtractionMethod

router = APIRouter()

@router.post("/pdf-extraction")
async def pdf_extraction(request: PdfRequestModel):
    """
    Endpoint to trigger PDF extraction.
    Args:
        pdf_title (str): The title of a PDF file.
    Returns:
        dict: Status of the extraction process.
    """
    topic = 'pdf_extraction_topic'
    message = {
        "archive_name": request.archive_name,
        "section_pattern": request.section_pattern
    }
    send_to_kafka(ExtractionMethod.STANDARD, message)
    return {"status": "PDF extraction triggered"}

