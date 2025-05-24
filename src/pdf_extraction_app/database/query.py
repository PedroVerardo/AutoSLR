from .session import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sentence_transformers import *
import logging
from ..models import Article, Segment, Chunk
import json
from typing import Tuple, Dict, List, Union
from sqlalchemy import text

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

def get_segments_by_article_id(db: Session, article_id: list[int]) -> tuple[bool, list[Segment]]:
    try:
        segments = db.query(Segment).filter(Segment.article_id.in_(article_id)).all()
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

def get_segments_by_title_and_articleid(db: Session, title: str, article_ids: list[int]) -> tuple[bool, list[Segment]]:
    try:
        segments = db.query(Segment).filter(Segment.segment_title.like(f"%{title}%"), Segment.article_id.in_(article_ids)).all()
        if not segments:
            return True, f"No segments found with title '{title}' and article IDs {article_ids}."
        return False, segments
    except Exception as e:
        return True, f"Error fetching segments: {e}"
    

def get_segments_by_title_vector_proximity_and_articleid(db: Session,
                                                         title_vector: list[float],
                                                         article_ids: list[int],
                                                         distance_trashold: float,
                                                         segment_limit: int = None) -> tuple[bool, dict[int, list[dict]]]:
    """
    The main idea is to give flexibility to the user to choose the distance threshold and the number of segments to return.
    This leads the other part of the code to get only 1 segment or the closest segments to the title vector.
    """
    try:
        query = db.query(
            Segment.id,
            Segment.segment_title,
            Segment.segment_title_vector.op('<->')(title_vector).label('distance')
        ).filter(
            Segment.article_id.in_(article_ids),
            #Segment.segment_title_vector.op('<->')(title_vector) <= distance_trashold
        ).order_by(text('distance'))
        
        if segment_limit is not None:
            query = query.limit(segment_limit)
        
        segments = query.all()
        
        if not segments:
            return True, f"No segments found with title vector proximity for the provided article IDs."
        
        grouped_segments = {}
        for segment in segments:
            if segment[0] not in grouped_segments:
                grouped_segments[segment[0]] = []
            grouped_segments[segment[0]].append({
                "title": segment[1],
                "distance": segment[2],
            })
            
        return False, grouped_segments
    except Exception as e:
        return True, f"Error fetching segments: {e}"
    
def get_chunk_text_by_vector_proximity(db: Session, question_text_vector: list[float], vector_distance: float, article_ids: list[int], limit: int = None) -> tuple[bool, dict[int, list[dict]]]:
    try:
        query = db.query(
            Chunk.segment_id,
            Chunk.id,
            Chunk.chunk_text,
            Chunk.chunk_vector.op('<->')(question_text_vector).label('distance')
        ).filter(
            Chunk.segment_id.in_(article_ids),
            Chunk.chunk_vector.op('<->')(question_text_vector) <= vector_distance
        ).order_by('distance')

        
        if limit is not None:
            query = query.limit(limit)
        
        chunks = query.all()
        
        grouped_chunks = {}
        for chunk in chunks:
            if chunk[0] not in grouped_chunks:
                grouped_chunks[chunk[0]] = []
            grouped_chunks[chunk[0]].append({
                "id": chunk[1],
                "text": chunk[2],
                "distance": chunk[3]
            })
            
        if not grouped_chunks:
            return True, f"No text proximity with this question and within the distance threshold {vector_distance} for the provided segment IDs."
        
        return False, grouped_chunks
    except Exception as e:
        return True, f"Error fetching chunks: {e}"
    
def get_segments_raw_sql(
    db: Session,
    title_vector: list[float],
    article_ids: list[int],
    distance_threshold: float,
    only_ids: bool = True,
) -> Tuple[bool, Union[Dict[int, List[Dict]], str]]:
    """
    Get segments using raw SQL to avoid ORM issues
    """
    try:
        if not article_ids:
            return True, "No article IDs provided"

        article_ids_str = ','.join(str(id) for id in article_ids)
        
        sql = f"""
        SELECT s.id, s.article_id, s.segment_title, 
               s.segment_title_vector <-> :vector AS distance
        FROM segment s
        WHERE s.article_id IN ({article_ids_str})
        ORDER BY distance
        """
        
        vector_str = json.dumps(title_vector)

        result = db.execute(text(sql), {
            "vector": vector_str,
            "threshold": distance_threshold
        })
        
        rows = result.fetchall()
        if not rows:
            return True, "No article id segments found"
            
        grouped_segments = {}
        for row in rows:
            article_id = int(row[1])
            if article_id not in grouped_segments:
                grouped_segments[article_id] = {
                    "id": [],
                    "title": [],
                    "distance": []
                }
                
            grouped_segments[article_id]["id"].append(int(row[0]))
            grouped_segments[article_id]["title"].append(row[2])
            grouped_segments[article_id]["distance"].append(float(row[3]) if row[3] is not None else 0.0)
            
            
        return False, grouped_segments
        
    except Exception as e:
        return True, f"Error in raw SQL approach: {e}"


def get_chunk_text_by_vector_proximity_raw_sql(
    db: Session,
    question_text_vector: list[float],
    segment_ids: list[int],
    limit: int = None
):
    """
    Get chunks by vector proximity using raw SQL to avoid ORM issues
    """
    try:
        if not segment_ids:
            return True, "No segment IDs provided"
            
        if not isinstance(question_text_vector, list):
            try:
                question_text_vector = list(question_text_vector)
            except:
                return True, f"Could not convert question_text_vector to list: {type(question_text_vector)}"
        
        segment_ids_str = ','.join(str(id) for id in segment_ids)
        
        sql = f"""
        SELECT c.segment_id, c.id, c.chunk_text, 
               c.chunk_vector <-> :vector AS distance
        FROM chunks c
        WHERE c.segment_id IN ({segment_ids_str})
        ORDER BY distance
        """
        
        vector_str = json.dumps(question_text_vector)
        
        result = db.execute(text(sql), {
            "vector": vector_str,
        })
        
        rows = result.fetchall()
        if not rows:
            return True, f"No text proximity with this question and within the distance threshold for the provided segment IDs."
            
        grouped_chunks = {}
        for row in rows:
            segment_id = int(row[0])
            if segment_id not in grouped_chunks:
                grouped_chunks[segment_id] = {
                    "id": [],
                    "text": [],
                    "distance": []
                }
            
            grouped_chunks[segment_id]["id"].append(int(row[1]) if row[1] is not None else 0)
            grouped_chunks[segment_id]["text"].append(row[2] if row[2] is not None else "No text available")
            grouped_chunks[segment_id]["distance"].append(float(row[3]) if row[3] is not None else 0.0)
            
        return False, grouped_chunks
        
    except Exception as e:
        return True, f"Error in raw SQL chunk approach: {e}"
    
