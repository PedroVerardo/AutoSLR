from confluent_kafka import Consumer, Producer
from fastapi.encoders import jsonable_encoder
from extraction_route import extract_text_with_metadata_route
from pdf_extraction_app.database.database import engine, Base
from models import ExtractTextRequest
import asyncio
import json

consumer_conf = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'pdf-extraction-group',
    'auto.offset.reset': 'earliest'
}

producer_conf = {
    'bootstrap.servers': 'localhost:9092',
    'client.id': 'python-producer'
}

consumer = Consumer(consumer_conf)
producer = Producer(producer_conf)

def delivery_report(err, msg):
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))

async def process_message(message):
    try:
        data = json.loads(message)
        archive_name = data.get("archive_name")
        section_pattern = data.get("section_pattern")
        
        request = ExtractTextRequest(archive_name=archive_name, section_pattern=section_pattern)
        
        response = await extract_text_with_metadata_route(request)
        
        result_topic = data.get("result_topic", "extraction-results")
        producer.produce(result_topic, json.dumps(jsonable_encoder(response)), callback=delivery_report)
        producer.flush()
    except Exception as e:
        print(f"Error processing message: {e}")

def consume_messages():
    consumer.subscribe(['pdf-extraction-requests'])
    print("Consumer is listening for messages...")
    
    try:
        while True:
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print("Consumer error: {}".format(msg.error()))
                continue
            
            asyncio.run(process_message(msg.value().decode('utf-8')))
    except KeyboardInterrupt:
        print("Consumer stopped.")
    finally:
        consumer.close()

if __name__ == "__main__":
    consume_messages()

