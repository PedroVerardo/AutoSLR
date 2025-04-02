from fastapi import HTTPException, APIRouter
import os
from ..utils.extrac_text import extract_text_with_metadata
from ..utils.chunking import ChunkText
from ..models import ExtractTextRequest, ExtractTextBatchRequest, Article, Segment, Chunk
from ..database import get_db
import requests
from datetime import datetime
import logging

router = APIRouter()
embed_url = os.getenv("TEXT_EMBEDDINGS_URL","") #http://127.0.0.1:8080/embed
headers = {
        "Content-Type": "application/json"
}
papers_pdf_path = os.getenv("PAPERS_PDF_PATH", "/home/pedro/Documents/Rag_test/grpc/papers_pdf")
logging.basicConfig(level=logging.CRITICAL, format='%(asctime)s - %(levelname)s - %(message)s')

@router.post("/article/extract_text")
async def extract_text_with_metadata_route(request: ExtractTextRequest):
    db = get_db()
    archive_name = request.archive_name
    section_pattern = request.section_pattern
    chunker = ChunkText("oi")
    
    existing_article = db.query(Article).filter(Article.title == archive_name).first()
    if existing_article:
        segments = db.query(Segment).filter(Segment.article_id == existing_article.id).all()
        return {
            "text": [
                {
                    "title": segment.segment_title,
                    "content": segment.segment_text
                } for segment in segments
            ]
        }
    
    
    
    direct_path = os.path.join(papers_pdf_path, archive_name)
    if os.path.isfile(direct_path):
        archive_path = direct_path
    else:
        archive_path = None
        for root, dirs, files in os.walk(papers_pdf_path):
            if archive_name in files:
                archive_path = os.path.join(root, archive_name)
                break
    
    if not archive_path:
        raise HTTPException(status_code=404, detail=f"Archive '{archive_name}' not found in {papers_pdf_path}")
    
    try:
        text = extract_text_with_metadata(archive_path, section_pattern)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing archive '{archive_name}': {str(e)}")
    
    if not text:
        raise HTTPException(status_code=404, detail=f"No text found in archive '{archive_name}' with the given section pattern '{section_pattern}'")
    
    # Create new article
    new_article = Article(
        title=archive_name,
        upload_date=datetime.now()
    )
    db.add(new_article)
    db.flush()
    
    for segment in text:
        payload = {"inputs": [segment["title"]]}
        new_segment = Segment(
            article_id=new_article.id,
            segment_title=segment["title"],
            segment_title_vector=None,
            segment_text=segment["content"],
        )
        
        # response = requests.post(embed_url, headers=headers, json=payload)
        # response_data = response.json()
        # vectors = response_data
        # new_segment.segment_title_vector = vectors[0]
        
        db.add(new_segment)
        db.flush() 
        
        
        chunk_list = ChunkText.fixed_window_splitter(segment["content"], 256)
        for chunk in chunk_list:
            # payload = {"inputs": [chunk]}
            # response = requests.post(embed_url, headers=headers, json=payload)
            # response_data = response.json()
            # vectors = response_data[0]
            
            new_chunk = Chunk(
                segment_id=new_segment.id,
                chunk_text=chunk,
                chunk_vector=None
            )
            db.add(new_chunk)
    
    
    db.commit()
    db.close()
    
    return {"text": text}

@router.post("/article/extract_folder")
async def extract_text_with_metadata_batch(request: ExtractTextBatchRequest):
    section_pattern = request.section_pattern
    subdirectory = request.directory

    papers_pdf_path = os.getenv("PAPERS_PDF_PATH","/home/pedro/Documents/Rag_test/grpc/papers_pdf")
    target_directory = os.path.join(papers_pdf_path, subdirectory)

    if not os.path.isdir(target_directory):
        raise HTTPException(status_code=404, detail=f"Subdirectory '{subdirectory}' not found in {papers_pdf_path}")

    results = []

    for root, dirs, files in os.walk(target_directory):
        for file in files:
            if file.lower().endswith('.pdf'):
                archive_path = os.path.join(root, file)
                try:
                    text = extract_text_with_metadata(archive_path, section_pattern)
                    results.append({
                        "file_name": file,
                        "full_path": archive_path,
                        "text": text
                    })
                except Exception as e:
                    results.append({
                        "file_name": file,
                        "full_path": archive_path,
                        "error": str(e)
                    })

    if not results:
        raise HTTPException(status_code=404, detail=f"No PDF files found in {papers_pdf_path}")

    return {"results": results}

@router.get("/article/{article_name}")
async def get_article(article_name: str):
    db = get_db()
    article = db.query(Article).filter(Article.title == article_name).first()
    if not article:
        raise HTTPException(status_code=404, detail=f"Article '{article_name}' not found")
    
    segments = db.query(Segment).filter(Segment.article_id == article.id).all()
    db.close()

    return {
        "title": article.title,
        "upload_date": article.upload_date,
        "segments": [
            {
                "title": segment.segment_title,
                "content": segment.segment_text
            } for segment in segments
        ]
    }

@router.put("/article/{article_name}")
async def update_article(article_name: str, request: ExtractTextRequest):
    db = get_db()
    article = db.query(Article).filter(Article.title == article_name).first()
    if not article:
        raise HTTPException(status_code=404, detail=f"Article '{article_name}' not found")
    
    section_pattern = request.section_pattern
    archive_path = os.path.join(os.getenv("PAPERS_PDF_PATH"), article_name)

    try:
        text = extract_text_with_metadata(archive_path, section_pattern)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error processing archive '{article_name}': {str(e)}")

    if not text:
        raise HTTPException(status_code=404, detail=f"No text found in archive '{article_name}' with the given section pattern '{section_pattern}'")

    for segment in text:
        new_segment = Segment(
            article_id=article.id,
            segment_title=segment["title"],
            segment_title_vector=None,
            segment_text=segment["content"],
            segment_text_vector=None
        )
        db.add(new_segment)

    db.commit()
    db.close()

    return {"text": text}

@router.delete("/article/{id}")
async def delete_article(article_name: str):
    db = get_db()
    article = db.query(Article).filter(Article.id == id).first()
    if not article:
        raise HTTPException(status_code=404, detail=f"Article '{article_name}' not found")
    
    segments = db.query(Segment).filter(Segment.article_id == article.id).all()
    for segment in segments:
        db.delete(segment)
    
    db.delete(article)
    db.commit()
    db.close()

    return {"detail": f"Article '{article_name}' and its segments deleted successfully"}
# Run the application using a command like `uvicorn extraction_route:app --reload`
