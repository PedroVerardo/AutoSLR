from flask import Flask

from extrac_text import extract_text_with_metadata
from flask import request
import os

app = Flask("literature_review_app")

@app.route("/extract_text_with_metadata", methods=["POST"])
def extract_text_with_metadata_route():
    archive_name = request.json.get("archive_name")
    section_pattern = request.json.get("section_pattern")
    
    if not archive_name:
        return {"error": "archive_name is required"}, 400
    
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
            return {"error": f"Archive '{archive_name}' not found in {papers_pdf_path}"}, 404
    
    text = extract_text_with_metadata(archive_path, section_pattern or "numeric_point_section")
    return {"text": text}

@app.route("/extract_text_with_metadata_batch", methods=["POST"])
def extract_text_with_metadata_batch():

    section_pattern = request.json.get("section_pattern", "numeric_point_section")
    subdirectory = request.json.get("subdirectory", "")

    papers_pdf_path = "/home/pedro/Documents/Rag_test/grpc/papers_pdf"
    
    target_directory = os.path.join(papers_pdf_path, subdirectory)
    
    if not os.path.isdir(target_directory):
        return {"error": f"Subdirectory '{subdirectory}' not found in {papers_pdf_path}"}, 404
    
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
        return {"error": f"No PDF files found in {papers_pdf_path}"}, 404
    
    return {"results": results}

if __name__ == "__main__":
    app.run(debug=True)


