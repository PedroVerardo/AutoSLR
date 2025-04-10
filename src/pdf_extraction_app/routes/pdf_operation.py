from fastapi import APIRouter
from database import get_db, get_article_by_id

router = APIRouter()
db = get_db()


@router.get("/{pdf_id}")
async def find_paper(pdf_id: str):
    get_article_by_id(db, pdf_id)
    return 