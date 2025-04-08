from pydantic import BaseModel

class PdfRequestModel(BaseModel):
    archive_name: str
    #extraction_method: str
    section_pattern: str