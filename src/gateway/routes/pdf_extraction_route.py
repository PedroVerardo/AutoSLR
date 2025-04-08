from fastapi import APIRouter, Depends 
from confluent_kafka import Producer
import json
import os
from typing import Dict, Any

from ..models import PdfRequestModel

router = APIRouter()

def get_kafka_producer():
    producer_config = {
        'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
        'client.id': 'pdf_producer'
    }
    return Producer(producer_config)

def send_to_kafka(producer: Producer, topic: str, message: Dict[str, Any]):
    producer.produce(topic, key="key", value=json.dumps(message))
    producer.flush()

@router.post("/pdf-extraction")
async def pdf_extraction(request: PdfRequestModel, producer: Producer = Depends(get_kafka_producer)):
    """
    Endpoint to trigger PDF extraction.
    Args:
        pdf_title (str): The title of a PDF file.
    Returns:
        dict: Status of the extraction process.
    """
    topic = 'pdf_topic'
    message = {
        "archive_name": request.archive_name,
        #"extraction_method": request.extraction_method,
        "section_pattern": request.section_pattern
    }
    send_to_kafka(producer, topic, message)
    return {"status": "PDF extraction triggered"}