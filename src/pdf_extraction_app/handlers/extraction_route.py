from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import os
from pdf_extraction_app.utils.extrac_text import extract_text_with_metadata

class ExtractTextRequest(BaseModel):
    archive_name: str
    section_pattern: str = "numeric_point_section"

class ExtractTextBatchRequest(BaseModel):
    section_pattern: str = "numeric_point_section"
    subdirectory: str = ""

@app.post("/extract_text_with_metadata")
async def extract_text_with_metadata_route(request: ExtractTextRequest):
    archive_name = request.archive_name
    section_pattern = request.section_pattern

    papers_pdf_path = "/home/pedro/Documents/Rag_test/grpc/papers_pdf"
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

    text = extract_text_with_metadata(archive_path, section_pattern)
    return {"text": text}

@app.post("/extract_text_with_metadata_batch")
async def extract_text_with_metadata_batch(request: ExtractTextBatchRequest):
    section_pattern = request.section_pattern
    subdirectory = request.subdirectory

    papers_pdf_path = "/home/pedro/Documents/Rag_test/grpc/papers_pdf"
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

# Run the application using a command like `uvicorn extraction_route:app --reload`
