from qdrant_client import QdrantClient
from qdrant_client.models import Distance
import logging


client = QdrantClient(url="http://localhost:6333")

def collection_exists(name: str) -> bool:
    try:
        collections = client.get_collections().collections
        return any(collection.name == name for collection in collections)
    except Exception as e:
        return False

def __create_collection(name: str, size: int = 256, distance: Distance = Distance.COSINE):

    try:
        client.create_collection(
            collection_name=name 
        )
    except Exception as e:
        logging.error(f"Error creating collection: {e}")
        return 1
    
    return 0

def create_collection(name: str, size: int = 256, distance: Distance = Distance.COSINE):
    if collection_exists(name):
        return 1
    return __create_collection(name, size, distance)

def insert_vector(collection_name: str,documents: list[str], metadatas: list[dict], ids: list[int]):

    try:
        client.add(
            ids=ids,
            collection_name=collection_name,
            documents=documents,
            metadata=metadatas,
        )
    except Exception as e:
        logging.error(f"Error inserting vector: {e}")
        return 0
    
    return 1

def query_vector(collection_name: str, text: str, top_k: int = 5):
    try:
        response = client.query(
            collection_name=collection_name,
            query_text=text,
        )
    except Exception as e:
        logging.error(f"Error querying collection: {e}")
        return 0
    
    return response





