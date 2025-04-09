from .session import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging
from ..models import Article, Segment, Chunk


logging.basicConfig(level=logging.INFO)

def insert_article(db: Session, article: Article, auto_commit: bool=False):
    try:
        db.add(article)
        db.flush()  
        
        if auto_commit:
            db.commit()
            
        return True, article.id
    except IntegrityError:
        db.rollback()
        return False, f"Article with title '{article.title}' already exists."
    except Exception as e:
        db.rollback()
        return False, f"Error inserting article: {e}"

def insert_segment(db: Session, segment: Segment, auto_commit: bool=False):
    if not segment.article_id:
        return False, "Segment must have an article_id"
    
    try:
        db.add(segment)
        db.flush()  
        
        if auto_commit:
            db.commit()
            
        return True, segment.id
    except Exception as e:
        db.rollback()
        return False, f"Error inserting segment: {e}"

def insert_chunk(db: Session, chunk: Chunk, auto_commit: bool=False):
    if not chunk.segment_id:
        return False, "Chunk must have a segment_id"
    
    try:
        db.add(chunk)
        db.flush()  
        
        if auto_commit:
            db.commit()
            
        return True, chunk.id
    except Exception as e:
        db.rollback()
        return False, f"Error inserting chunk: {e}"
    
def insert_article_with_segments(db: Session, article: Article, segments: list[Segment]):
    try:
        article_success, article_result = insert_article(db, article)
        if not article_success:
            db.rollback()
            return False, article_result
        
        for segment in segments:
            segment.article_id = article.id
            segment_success, segment_result = insert_segment(db, segment)
            if not segment_success:
                db.rollback()
                return False, segment_result
        
        db.commit()
        return True, "Successfully inserted article with segments"
    except Exception as e:
        db.rollback()
        return False, f"Error during insertion: {e}"
    
def insert_article_with_segments_and_chunks(db: Session, article: Article, segments: list[Segment], chunks_list: list[list[Chunk]]):
    try:
        article_success, article_result = insert_article(db, article)
        if not article_success:
            db.rollback()
            return False, article_result
        
        for i, segment in enumerate(segments):
            segment.article_id = article.id
            segment_success, segment_result = insert_segment(db, segment)
            if not segment_success:
                db.rollback()
                return False, segment_result
            
            if i < len(chunks_list):
                for chunk in chunks_list[i]:
                    chunk.segment_id = segment.id
                    chunk_success, chunk_result = insert_chunk(db, chunk)
                    if not chunk_success:
                        db.rollback()
                        return False, chunk_result
        
        db.commit()
        return True, "Successfully inserted article with segments and chunks"
    except Exception as e:
        db.rollback()
        return False, f"Error during insertion: {e}"