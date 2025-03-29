from pydantic import BaseModel

class ExtractTextRequest(BaseModel):
    archive_name: str
    section_pattern: str = "numeric_point_section"

class ExtractTextBatchRequest(BaseModel):
    directory: str
    section_pattern: str = "numeric_point_section"