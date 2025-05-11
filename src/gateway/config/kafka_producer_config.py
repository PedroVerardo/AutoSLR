import os
from typing import Dict, Any
import json

from .pdf_enumns import ExtractionMethod
from confluent_kafka import Producer

def get_base_kafka_config() -> Dict[str, Any]:
    """Return base Kafka producer configuration."""
    return {
        'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
        'client.id': 'gateway_producer',
    }

PRODUCER_CONFIG = {
    ExtractionMethod.STANDARD: {
        "topic": "pdf_extraction_topic",
        "producer_config": {
            **get_base_kafka_config(),
        }
    },
    ExtractionMethod.CRUD: {
        "topic": "pdf_crud_topic",
        "producer_config": {
            **get_base_kafka_config(),
        }
    }
}

def get_producer_config(extraction_method: ExtractionMethod) -> Dict[str, Any]:
    """
    Get producer configuration for a specific extraction method.
    Falls back to standard configuration if the method is not found.
    """
    return PRODUCER_CONFIG.get(
        extraction_method, 
        PRODUCER_CONFIG[ExtractionMethod.STANDARD]
    )

def get_producer(extraction_method: ExtractionMethod) -> Producer:
    """
    Get a Kafka producer instance based on the extraction method.
    Args:
        extraction_method (ExtractionMethod): The extraction method to determine the producer configuration.
    Returns:
        Producer: Configured Kafka producer instance.
    """
    config = get_producer_config(extraction_method)["producer_config"]
    return Producer(config)

def send_to_kafka(extraction_method: ExtractionMethod, message: Dict[str, Any]):
    """
    Send a message to Kafka based on the extraction method.
    Args:
        extraction_method (ExtractionMethod): The extraction method to determine the topic and producer configuration.
        message (Dict[str, Any]): The message to send to Kafka.
    """
    producer_config = get_producer_config(extraction_method)
    topic = producer_config["topic"]
    producer = get_producer(extraction_method)
    producer.produce(topic, key="key", value=json.dumps(message))
    producer.flush()