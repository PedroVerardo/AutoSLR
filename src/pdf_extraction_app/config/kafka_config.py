import os
from typing import Dict, Callable, Any
from ..models import ServiceType

class KafkaConfig:
    """Configuration for Kafka connections and topic mappings"""
    
    BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    CLIENT_ID = os.getenv('KAFKA_CLIENT_ID', 'gateway_producer')
    
    TOPIC_MAPPING: Dict[str, str] = {
        ServiceType.PDF_EXTRACTION: os.getenv('PDF_TOPIC', 'pdf_extraction_topic'),
        ServiceType.CRUD_INTERACTION: os.getenv('QUESTION_TOPIC', 'pdf_question_topic'),
    }
    
    @staticmethod
    def get_consumer_config():
        return {
            'bootstrap.servers': KafkaConfig.BOOTSTRAP_SERVERS,
            'group.id': os.getenv('KAFKA_GROUP_ID', 'pdf_consumer_group'),
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': True,
        }
        
    @staticmethod
    def get_topic_for_service(service_type: str) -> str:
        if service_type not in KafkaConfig.TOPIC_MAPPING:
            raise ValueError(f"Unknown service type: {service_type}")
        return KafkaConfig.TOPIC_MAPPING[service_type]