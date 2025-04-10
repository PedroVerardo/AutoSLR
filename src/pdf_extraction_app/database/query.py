from .session import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging
from ..models import Article, Segment, Chunk

logging.basicConfig(level=logging.INFO)

def get_article_by_id(db: Session, article_id: int):
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            return True, f"Article with id '{article_id}' does not exist."
        return False, article
    except Exception as e:
        return True, f"Error fetching article: {e}"
    
def get_segment_by_id(db: Session, segment_id: int):
    try:
        segment = db.query(Segment).filter(Segment.id == segment_id).first()
        if not segment:
            return True, f"Segment with id '{segment_id}' does not exist."
        return False, segment
    except Exception as e:
        return True, f"Error fetching segment: {e}"

def get_chunk_by_id(db: Session, chunk_id: int):
    try:
        chunk = db.query(Chunk).filter(Chunk.id == chunk_id).first()
        if not chunk:
            return True, f"Chunk with id '{chunk_id}' does not exist."
        return False, chunk
    except Exception as e:
        return True, f"Error fetching chunk: {e}"
    
