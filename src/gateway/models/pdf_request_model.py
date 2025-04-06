from pydantic import BaseModel

class PdfRequestModel(BaseModel):
    archive_name: str
    section_pattern: str