from confluent_kafka import Consumer, KafkaError, Producer
from confluent_kafka.admin import AdminClient, NewTopic
import numpy as np

import json
import time
import os
import logging
import datetime

from .pdf_handler import PDFHandler
from ..config.kafka_config import producer_config
from ..database import insert_article, insert_segment, insert_chunk, batch_insert_segments, batch_insert_chunks
from ..database import get_db
from ..models.db_table_model import Article, Segment, Chunk
from ..utils.chunking import ChunkText
from ..database.session import Base, engine

# TODO: Add logging configuration
# TODO: Add the separation between the embedding and the pdf extraction

db = get_db()

def process_message(message):
    """
    Process the Kafka message, extract titles from the PDF, and return them.

    Args:
        message (dict): The Kafka message containing the PDF path.

    Returns:
        list[str]: A list of titles extracted from the PDF.
    """
    archive_name = message.get("archive_name")
    section_pattern = message.get("section_pattern")
    data_path = os.getenv('DATA_PATH', '/home/pedro/Documents/Rag_test/grpc/papers_pdf')

    pdf_path = None

    for root, dirs, files in os.walk(data_path):
        for file in files:
            if archive_name in file and file.lower().endswith('.pdf'):
                pdf_path = os.path.join(root, file)
                logging.info(f"Found matching PDF: {pdf_path}")
                break
    
    if pdf_path is None:
        logging.error(f"PDF file not found for title: {archive_name}")
        return []

    doc = PDFHandler.try_open(pdf_path)

    if not doc:
        print(f"Failed to open PDF: {pdf_path}")
        return []
    
    tag = "bold"
    
    text, _ = PDFHandler.tagged_extraction(doc, tag)
    if not text:
        logging.error(f"Failed to extract text from PDF: {pdf_path}")
        return []

    extracted_text = PDFHandler.extract_text_with_regex(text, section_pattern)

    if not extracted_text:
        logging.error(f"No text extracted using regex pattern: {section_pattern}")
        return []

    titles = [value['title'] for value in extracted_text.values()]
    qtd = len(titles)
    doc.close()

    ####### Insert into DB #######

    segment_buff = np.array([0] * qtd, dtype=Segment)

    Article_obj = Article(
        title=archive_name,
        upload_date=datetime.date.fromtimestamp(time.time()),
    )

    err, info = insert_article(db, Article_obj, auto_commit=True)
    if err:
        logging.error(f"Error inserting article: {info}")
        return []
    
    for idx, (key, value) in enumerate(extracted_text.items()):
        segment_obj = Segment(
            article_id=Article_obj.id,
            segment_title=value['title'],
            segment_text=value['text'],
        )

        segment_buff[idx] = segment_obj

        chunk_list = ChunkText.fixed_window_splitter(value['text'], 384)
        qtd = len(chunk_list)
        chunk_buff = np.array([0] * qtd, dtype=Chunk)

        for chunk in chunk_list:
            chunk_obj = Chunk(
                segment_id=segment_obj.id,
                chunk_text=chunk,
            )
            chunk_buff.append(chunk_obj)
        


        err, info = batch_insert_segments(db, segment_obj, auto_commit=True)
        err, info = insert_chunk(db, chunk_buff, auto_commit=True)
        if err:
            logging.error(f"Error inserting chunk: {info}")
            return []
        


        


    return titles

def ensure_topic_exists(topic_name, bootstrap_servers):
    admin_client = AdminClient({'bootstrap.servers': bootstrap_servers})
    topic_metadata = admin_client.list_topics(timeout=10)
    if topic_name not in topic_metadata.topics:
        print(f"Creating topic: {topic_name}")
        new_topic = NewTopic(topic_name, num_partitions=1, replication_factor=1)
        admin_client.create_topics([new_topic])
    else:
        print(f"Topic {topic_name} already exists.")

def main():
    """
    Main function to consume messages from Kafka and process them.
    """
    consumer_config = {
        'bootstrap.servers': os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092'),
        'group.id': 'pdf_consumer_group',
        'auto.offset.reset': 'earliest'
    }

    consumer = Consumer(consumer_config)

    try:
        consumer.subscribe(['pdf_topic'])

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
                print(f"Received message: {message_value}")
                titles = process_message(message_value)
                if titles:
                    print("Extracted Titles:")
                    for title in titles:
                        print(f"- {title}")
                else:
                    print("No titles found.")
            except json.JSONDecodeError:
                print("Failed to decode message as JSON.")

    except KeyboardInterrupt:
        print("Consumer interrupted by user.")
    finally:
        db.close()
        consumer.close()

if __name__ == "__main__":
    with engine.begin() as connection:
        for table in reversed(Base.metadata.sorted_tables):
            connection.execute(table.delete())

    Base.metadata.create_all(bind=engine)
    ensure_topic_exists('pdf_topic', 'localhost:9092')
    time.sleep(5)
    main()