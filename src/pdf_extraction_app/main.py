from database import engine, Base
from confluent_kafka import Producer

#Base.metadata.create_all(bind=engine)

conf = {
    'bootstrap.servers': 'localhost:9092',
    'client.id': 'python-producer'
}

producer = Producer(conf)

def delivery_report(err, msg):
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message delivered to {} [{}]'.format(msg.topic(), msg.partition()))


def produce_message(topic, message):
    producer.produce(topic, message, callback=delivery_report)
    producer.poll(0)
    producer.flush()

if __name__ == "__main__":
    produce_message("test", "Hello World!")

