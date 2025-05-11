from pydantic import BaseModel
from typing import Dict, Any

class PdfRequestModel(BaseModel):
    archive_name: str
    #extraction_method: str
    section_pattern: str

class PdfQuestionData(BaseModel):
    question: str
    archive_ids: list[str]
    section_title: str
    feeding_method: str

class PdfQuestionModel(BaseModel):
    operation: str
    data: PdfQuestionData
    #extraction_method: str