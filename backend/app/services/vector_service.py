class VectorService:
    def index_document(self, document_id: int, content: str) -> dict:
        # Placeholder for FAISS/Qdrant indexing.
        return {"indexed": True, "document_id": document_id, "chars": len(content)}
