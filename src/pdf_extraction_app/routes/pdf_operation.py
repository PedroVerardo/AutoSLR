from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from fastapi import Depends
from sqlalchemy.orm import Session


from database import get_db, get_article_by_id, get_segment_by_id
from models import Article, Segment, Chunk

from typing import Dict, Any

router = APIRouter()
db = get_db()


def article_to_dict(pydanamic_obj) -> Dict[Any, Any]:
    """Convert SQLAlchemy model instance to a dictionary for JSON serialization."""
    if not pydanamic_obj:
        return {}
    
    result = {}
    for column in pydanamic_obj.__table__.columns:
        value = getattr(pydanamic_obj, column.name)
        if hasattr(value, 'isoformat'):
            value = value.isoformat()
        result[column.name] = value

    for relationship in pydanamic_obj.__mapper__.relationships:
        related_value = getattr(pydanamic_obj, relationship.key)
        if related_value is not None:
            if isinstance(related_value, list):  # Handle one-to-many relationships
                result[relationship.key] = [article_to_dict(item) for item in related_value]
            else:  # Handle one-to-one relationships
                result[relationship.key] = article_to_dict(related_value)

    return result


@router.get("pdf/{pdf_id}")
async def find_paper(pdf_id: str, db: Session = Depends(get_db)):
    err, article = get_article_by_id(db, pdf_id)
    
    if err:
        raise HTTPException(status_code=404, detail=str(err))
    
    article_dict = article_to_dict(article)
    
    return JSONResponse(content={"article_info": article_dict})

@router.get("/segment/{segment_id}")
async def find_segment(segment_id: int, db: Session = Depends(get_db)):
    err, segment = get_segment_by_id(db, segment_id)
    
    if err:
        raise HTTPException(status_code=404, detail=str(err))
    
    segment_dict = article_to_dict(segment)
    
    return JSONResponse(content={"segment_info": segment_dict})