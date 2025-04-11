from .session import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging
from ..models import Article, Segment, Chunk

logging.basicConfig(level=logging.INFO)

def get_article_by_id(db: Session, article_id: int) -> tuple[bool, Article]:
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            return True, f"Article with id '{article_id}' does not exist."
        return False, article
    except Exception as e:
        return True, f"Error fetching article: {e}"

def get_article_by_title(db: Session, title: str) -> tuple[bool, Article]:
    try:
        article = db.query(Article).filter(Article.title == title).all()
        if not article:
            return True, f"Article with title '{title}' does not exist."
        return False, article
    except Exception as e:
        return True, f"Error fetching article: {e}"
    
def get_segment_by_id(db: Session, segment_id: int) -> tuple[bool, Segment]:
    try:
        segment = db.query(Segment).filter(Segment.id == segment_id)
        if not segment:
            return True, f"Segment with id '{segment_id}' does not exist."
        return False, segment
    except Exception as e:
        return True, f"Error fetching segment: {e}"

def get_chunk_by_id(db: Session, chunk_id: int) -> tuple[bool, Chunk]:
    try:
        chunk = db.query(Chunk).filter(Chunk.id == chunk_id)
        if not chunk:
            return True, f"Chunk with id '{chunk_id}' does not exist."
        return False, chunk
    except Exception as e:
        return True, f"Error fetching chunk: {e}"

def get_some_articles(db: Session, offset: int = 0, limit: int = 10) -> tuple[bool, list[Article]]:
    try:
        articles = db.query(Article).offset(offset).limit(limit).all()
        if not articles:
            return True, "No articles found."
        return False, articles
    except Exception as e:
        return True, f"Error fetching articles: {e}"

def get_segments_by_article_id(db: Session, article_id: int) -> tuple[bool, list[Segment]]:
    try:
        segments = db.query(Segment).filter(Segment.article_id == article_id).all()
        if not segments:
            return True, f"No segments found for article id '{article_id}'."
        return False, segments
    except Exception as e:
        return True, f"Error fetching segments: {e}"

def get_chunks_by_segment_id(db: Session, segment_id: int) -> tuple[bool, list[Chunk]]:
    try:
        chunks = db.query(Chunk).filter(Chunk.segment_id == segment_id).all()
        if not chunks:
            return True, f"No chunks found for segment id '{segment_id}'."
        return False, chunks
    except Exception as e:
        return True, f"Error fetching chunks: {e}"

def get_segments_by_title_and_articleid(db: Session, title: str, article_id: int) -> tuple[bool, list[Segment]]:
    try:
        segments = db.query(Segment).filter(Segment.segment_title.like(f"%{title}%"), Segment.article_id == article_id).all()
        if not segments:
            return True, f"No segments found with title '{title}'."
        return False, segments
    except Exception as e:
        return True, f"Error fetching segments: {e}"
    
def get_segmentid_by_title_vector_proximity(db: Session, title_vector: str, vector_distance: float) -> tuple[bool, list[int]]:
    try:
        segments = db.query(Segment).filter(Segment.segment_title_vector.op('<->')(title_vector) <= vector_distance).all()
        segments = [segment.id for segment in segments]
        if not segments:
            return True, f"No segments found with title vector '{title_vector}'."
        return False, segments
    except Exception as e:
        return True, f"Error fetching segments: {e}"


    
