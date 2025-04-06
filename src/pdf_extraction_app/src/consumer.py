from confluent_kafka import Consumer, KafkaError
from confluent_kafka.admin import AdminClient, NewTopic

import json
import time
import os
import logging

from pdf_handler import PDFHandler

# TODO: change the print to logging or to opentelemetry
# TODO: thinking how to personalize the regex pattern with the specific tag
# TODO: implement the migration of the database

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

    # Initialize pdf_path to None
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
    
    section_pattern = fr"\n(\d)\.\s+(?!\d)[\w\s]+<--{tag}-->\n"

    extracted_text = PDFHandler.extract_text_with_regex(text, section_pattern)

    if not extracted_text:
        logging.error(f"No text extracted using regex pattern: {section_pattern}")
        return []

    titles = [value['title'] for value in extracted_text.values()]
    doc.close()
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
        consumer.close()

if __name__ == "__main__":
    ensure_topic_exists('pdf_topic', 'localhost:9092')
    time.sleep(5)
    main()