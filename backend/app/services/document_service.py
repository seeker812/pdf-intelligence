from sqlalchemy.orm import Session

from backend.app.core.exceptions import AppException
from backend.app.models.document import Document
from backend.app.schemas.document_schema import DocumentCreateRequest


class DocumentService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_document(self, payload: DocumentCreateRequest) -> Document:
        doc = Document(title=payload.title, content=payload.content, source=payload.source)
        self.db.add(doc)
        self.db.commit()
        self.db.refresh(doc)
        return doc

    def get_document(self, document_id: int) -> Document:
        doc = self.db.get(Document, document_id)
        if not doc:
            raise AppException(message=f"Document {document_id} not found", status_code=404, code="DOCUMENT_NOT_FOUND")
        return doc

    def list_documents(self) -> list[Document]:
        return self.db.query(Document).order_by(Document.id.desc()).all()
