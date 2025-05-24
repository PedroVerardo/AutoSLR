from confluent_kafka import Consumer, KafkaError, Producer
from confluent_kafka.admin import AdminClient, NewTopic
import numpy as np
import google.generativeai as genai
from dotenv import load_dotenv

import json
import time
import os
import logging
import datetime

from .pdf_handler import PDFHandler
from .pdf_crud_process import process_crud_message
from .pdf_extraction_process import process_extraction_message
from ..models import ServiceType
from ..config import KafkaConfig, EmbeddingConfig
from ..database import insert_article, insert_segment, insert_chunk, batch_insert_segments, batch_insert_chunks
from ..database import get_db
from ..models import Article, Segment, Chunk
from ..utils.chunking import ChunkText
from ..database.session import Base, engine

# TODO: Add logging configuration
# TODO: Add the separation between the embedding and the pdf extraction

db = get_db()

def ensure_topic_exists(topic_name, bootstrap_servers):
    admin_client = AdminClient({'bootstrap.servers': bootstrap_servers})
    topic_metadata = admin_client.list_topics(timeout=10)
    if topic_name not in topic_metadata.topics:
        print(f"Creating topic: {topic_name}")
        new_topic = NewTopic(topic_name, num_partitions=1, replication_factor=1)
        fs = admin_client.create_topics([new_topic])
        for topic, f in fs.items():
            try:
                f.result()
                print(f"Topic {topic} created successfully.")
            except Exception as e:
                print(f"Failed to create topic {topic}: {e}")
    else:
        print(f"Topic {topic_name} already exists.")

def main():
    """
    Main function to consume messages from Kafka and process them.
    """
    consumer = Consumer(KafkaConfig.get_consumer_config())
    model = EmbeddingConfig.load_embedding_model()
    data_path = os.getenv('DATA_PATH', '/home/pedro/Documents/Rag_test/grpc/papers_pdf')
    load_dotenv()
    genai.configure(api_key=os.environ["GEMINI_API_KEY"])

    llm_model = genai.GenerativeModel('gemini-1.5-flash')

    try:
        consumer.subscribe(['pdf_extraction_topic', 'pdf_crud_topic'])

        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF: 
                    continue
                else:
                    print(f"Consumer error: {msg.error()}")
                    break

            try:
                message_value = json.loads(msg.value().decode('utf-8'))
                topic = msg.topic()
                if topic == 'pdf_extraction_topic':
                    print(process_extraction_message(message_value, model,data_path, db))
                elif topic == 'pdf_crud_topic':
                    print(process_crud_message(message_value, model, llm_model, db))

            except json.JSONDecodeError:
                print("Failed to decode message as JSON.")

    except KeyboardInterrupt:
        print("Consumer interrupted by user.")
    finally:
        db.close()
        consumer.close()

if __name__ == "__main__":
    ensure_topic_exists('pdf_extraction_topic', 'localhost:9092')
    ensure_topic_exists('pdf_crud_topic', 'localhost:9092')

    with engine.begin() as connection:
        Base.metadata.create_all(bind=connection)

    time.sleep(5)
    main()
