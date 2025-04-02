from database import engine, Base
from confluent_kafka import Producer

#Base.metadata.create_all(bind=engine)