from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional

class ServiceType(str, Enum):
    """Enum of all supported service types"""
    PDF_EXTRACTION = "pdf_extraction"
    CRUD_INTERACTION = "crud_interaction"
    EMBEDDING_PROCESSING = "embedding_processing"

class BaseRequestModel(BaseModel):
    """Base model for all service requests"""
    service_type: Optional[ServiceType] = None
    priority: int = Field(default=1, ge=1, le=10) 
    request_id: Optional[str] = None 
    
    class Config:
        populate_by_field_name = True
        # # Example usage
        # data = {"first_name": "John", "last_name": "Doe"}
        # user = User(**data)  # Works because keys match field names