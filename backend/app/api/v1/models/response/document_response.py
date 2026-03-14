from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentUploadResponse(BaseModel):
    document_id: str
    status: str


class DocumentResponse(BaseModel):
    document_id: str
    file_name: str
    document_type: str | None
    category: str | None
    short_summary: str | None
    detailed_summary: str | None
    status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AskQuestionResponse(BaseModel):
    answer: str
    sources: list[str]


class DocumentInsightResponse(BaseModel):
    id: str
    document_id: str
    insight: str

    model_config = ConfigDict(from_attributes=True)


class DocumentChunkResponse(BaseModel):
    chunk_id: str
    document_id: str
    chunk_text: str
    chunk_index: int

    model_config = ConfigDict(from_attributes=True)
