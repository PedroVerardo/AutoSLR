from .session import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sentence_transformers import SentenceTransformer
import logging
from ..models import Article, Segment, Chunk, ChatHistory

logging.basicConfig(level=logging.INFO)

def insert_article(db: Session, article: Article, auto_commit: bool=False):
    try:
        db.add(article) 
        db.flush()
        
        if auto_commit:
            db.commit()
            
        return False, article.id
    except IntegrityError:
        db.rollback()
        return True, f"Article with title '{article.title}' already exists."
    except Exception as e:
        db.rollback()
        return True, f"Error inserting article: {e}"

def insert_segment(db: Session, segment: Segment, auto_commit: bool=False):
    if segment.article_id is None:
        return True, "Segment must have an article_id"
    
    try:
        db.add(segment)
        db.flush()
        
        if auto_commit:
            db.commit()
            
        return False, segment.id
    except Exception as e:
        db.rollback()
        return True, f"Error inserting segment: {e}"

def insert_chunk(db: Session, chunk: Chunk, auto_commit: bool=False):
    if chunk.segment_id is None:
        return True, "Chunk must have a segment_id"
    
    try:
        db.add(chunk)
        
        if auto_commit:
            db.commit()
            
        return False, chunk.id
    except Exception as e:
        db.rollback()
        return True, f"Error inserting chunk: {e}"
    
def insert_question_and_answer(db: Session, chat_history: ChatHistory, auto_commit: bool=False):
    if not chat_history.article_id:
        return True, "ChatHistory must be associated with one or more articles ids"
    
    try:
        db.add(chat_history)
        
        if auto_commit:
            db.commit()
            
        return False, chat_history.id
    except Exception as e:
        db.rollback()
        return True, f"Error inserting chat history: {e}"
    
def batch_insert_segments(db: Session, segment_objects: list[Segment], auto_commit=False):
    try:
        segment_values = [(seg.article_id, seg.segment_title, seg.segment_title_vector, seg.segment_text) for seg in segment_objects]
        
        cursor = db.connection().connection.cursor()
        cursor.executemany(
            "INSERT INTO segments (article_id, segment_title, segment_title_vector, segment_text) VALUES (%s, %s, %s, %s) RETURNING id", 
            segment_values
        )
        
        segment_ids = [row[0] for row in cursor.fetchall()]
        
        for i, segment_obj in enumerate(segment_objects):
            segment_obj.id = segment_ids[i]
            
        if auto_commit:
            db.commit()
            
        return False, segment_ids
        
    except Exception as e:
        if auto_commit:
            db.rollback()
        return True, str(e)

def batch_insert_chunks(db: Session, chunk_objects: list[Chunk], auto_commit=False):
    try:
        chunk_values = [(chunk.id, chunk.chunk_text, chunk.chunk_vector) for chunk in chunk_objects]
        
        cursor = db.connection().connection.cursor()
        cursor.executemany(
            "INSERT INTO chunks (segment_id, chunk_text, chunk_vector) VALUES (%s, %s, %s) RETURNING id", 
            chunk_values
        )
        
        chunk_ids = [row[0] for row in cursor.fetchall()]
        
        for i, chunk_obj in enumerate(chunk_objects):
            chunk_obj.id = chunk_ids[i]
            
        if auto_commit:
            db.commit()
            
        return False, chunk_ids
        
    except Exception as e:
        if auto_commit:
            db.rollback()
        return True, str(e)
    
def insert_question_and_answer(db: Session, chat_history: ChatHistory, auto_commit=False):
    if not chat_history.article_id:
        return True, "ChatHistory must be associated with one or more articles ids"
    
    try:
        db.add(chat_history)
        
        if auto_commit:
            db.commit()
            
        return False, chat_history.id
    except Exception as e:
        db.rollback()
        return True, f"Error inserting chat history: {e}"