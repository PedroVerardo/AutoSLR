from database import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging
from ..models import Article, Segment, Chunk

logging.basicConfig(level=logging.INFO)

async def delete_chunk(db: Session, segment_id: int):
    try:
        chunks = db.query(Chunk).filter(Chunk.segment_id == segment_id).all()
        if not chunks:
            return False, f"Chunk with id '{segment_id}' does not exist."
        
        for chunk in chunks:
            db.delete(chunk)
        db.commit()
        return True, f"Chunk with id '{segment_id}' deleted successfully."
    except Exception as e:
        db.rollback()
        return False, f"Error deleting chunk: {e}"
    
async def delete_segment(db: Session, article_id: int):
    try:
        segments = db.query(Segment).filter(Segment.article_id == article_id).all()
        if not segments:
            return False, f"Segment with id '{article_id}' does not exist."
        
        for segment in segments:
            db.delete(segment)
        db.commit()
        return True, f"Segment with id '{article_id}' deleted successfully."
    except Exception as e:
        db.rollback()
        return False, f"Error deleting segment: {e}"
    
async def delete_article(db: Session, article_id: int):
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            return False, f"Article with id '{article_id}' does not exist."
        db.delete(article)
        db.commit()
        return True, f"Article with id '{article_id}' deleted successfully."
    except Exception as e:
        db.rollback()
        return False, f"Error deleting article: {e}"
    
async def delete_article_with_segments(db: Session, article_id: int):
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            return False, f"Article with id '{article_id}' does not exist."
        
        segments = db.query(Segment).filter(Segment.article_id == article_id).all()
        if not segments:
            return False, f"Segment with id '{article_id}' does not exist."
        
        for segment in segments:
            db.delete(segment)
        db.delete(article)
        db.commit()
        return True, f"Article with id '{article_id}' and its segments deleted successfully."
    except Exception as e:
        db.rollback()
        return False, f"Error deleting article and segments: {e}"
    
async def delete_article_with_segments_and_chunks(db: Session, article_id: int):
    try:
        article = db.query(Article).filter(Article.id == article_id).first()
        if not article:
            return False, f"Article with id '{article_id}' does not exist."
        segments = db.query(Segment).filter(Segment.article_id == article_id).all()
        if not segments:
            return False, f"Segment with id '{article_id}' does not exist."
        for segment in segments:
            chunks = db.query(Chunk).filter(Chunk.segment_id == segment.id).all()
            if not chunks:
                return False, f"Chunk with id '{segment.id}' does not exist."
            for chunk in chunks:
                db.delete(chunk)
            db.delete(segment)
        db.delete(article)
        db.commit()
        return True, f"Article with id '{article_id}' and its segments and chunks deleted successfully."
    except Exception as e:
        db.rollback()
        return False, f"Error deleting article, segments, and chunks: {e}"
async def delete_all_articles(db: Session):
    try:
        articles = db.query(Article).all()
        if not articles:
            return False, "No articles to delete."
        for article in articles:
            db.delete(article)
        db.commit()
        return True, "All articles deleted successfully."
    except Exception as e:
        db.rollback()
        return False, f"Error deleting all articles: {e}"
    
async def delete_all_segments(db: Session):
    try:
        segments = db.query(Segment).all()
        if not segments:
            return False, "No segments to delete."
        for segment in segments:
            db.delete(segment)
        db.commit()
        return True, "All segments deleted successfully."
    except Exception as e:
        db.rollback()
        return False, f"Error deleting all segments: {e}"

async def delete_all_chunks(db: Session):
    try:
        chunks = db.query(Chunk).all()
        if not chunks:
            return False, "No chunks to delete."
        for chunk in chunks:
            db.delete(chunk)
        db.commit()
        return True, "All chunks deleted successfully."
    except Exception as e:
        db.rollback()
        return False, f"Error deleting all chunks: {e}"