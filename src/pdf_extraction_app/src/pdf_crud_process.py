import os

from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, Integer, String, Text, Date, ForeignKey, Float
import dotenv
from ..database import get_chunk_text_by_vector_proximity_raw_sql, get_chunk_text_by_vector_proximity, get_segments_raw_sql
from ..models import Article, Segment, Chunk, ChatHistory

def process_crud_message(message: dict, embed_model: SentenceTransformer, gen_model, db: Session) -> None:
    operation = message.get('operation')
    data = message.get('data')

    if operation == 'update':
        raise NotImplementedError("Update operation is not implemented yet.")
    elif operation == 'delete':
        raise NotImplementedError("Delete operation is not implemented yet.")
    elif operation == 'question':
        question_vector = embed_model.encode(data['question'], normalize_embeddings=True).flatten().tolist()
        title_vector = embed_model.encode(data['section_title'], normalize_embeddings=True).flatten().tolist()
        # print(f"Title vector: {title_vector}")
        # print(f"Type of title vector: {type(title_vector)}")
        # title_vector = [0.0] * 384

        err, grouped_segments = get_segments_raw_sql(db, title_vector, data['archive_ids'], 0.3)

        if err:
            print(f"Error fetching segments: {grouped_segments}")
            return None
        
        print(f"Grouped segments: {grouped_segments}")

        all_segment_ids = []
        for group in grouped_segments.keys():
            all_segment_ids.extend(grouped_segments[group]['id'])
            

        err, group_of_chunks = get_chunk_text_by_vector_proximity_raw_sql(
            db,
            question_vector,
            all_segment_ids,
            0.3
        )

        if err:
            print(f"Error fetching chunks: {group_of_chunks}")
            return None
        
        text = ''
        for segment_id, chunk_data in group_of_chunks.items():
            joined_text = '\n'.join(chunk_data['text']) + '\n'
            text += joined_text
            

        prompt = f"Based only in this text segments answare that question: {data['question']}\n"


        text += prompt
    
        
        print(f"Text: {text}")
        
        # response = gen_model.generate_content(text)
        
        # ch = ChatHistory(
        #     article_id=data['article_id'],
        #     question=data['question'],
        #     answer=response,
        #     segments=group_of_chunks.keys()
        # )

        # insert_question_and_answer(db, ch, auto_commit=True)

    else:
        print(f"Unknown operation: {operation}")


def handle_create(data):
    # Logic for handling 'create' operation
    print(f"Creating resource with data: {data}")


def handle_update(data):
    # Logic for handling 'update' operation
    print(f"Updating resource with data: {data}")


def handle_delete(data):
    # Logic for handling 'delete' operation
    print(f"Deleting resource with data: {data}")