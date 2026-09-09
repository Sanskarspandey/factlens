"""Document schemas for request and response serialization."""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.models.document import DocumentStatus


class DocumentPageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    page_number: int
    raw_text: str
    layout_blocks: Optional[List[Dict[str, Any]]] = None


class DocumentBase(BaseModel):
    filename: str
    file_size: int
    num_pages: int = 0
    metadata_json: Optional[Dict[str, Any]] = None


class DocumentCreate(DocumentBase):
    file_path: str
    file_hash: str


class DocumentRead(DocumentBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    file_path: str
    file_hash: str
    status: DocumentStatus
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    fact_count: Optional[int] = 0


class DocumentDetailRead(DocumentRead):
    pages: List[DocumentPageRead] = []
