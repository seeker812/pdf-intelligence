from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, VectorParams, Distance
import uuid


class QdrantService:
    """
    Handles storage and retrieval of embeddings in Qdrant.
    """

    def __init__(self):

        self.collection_name = "document_chunks"

        self.client = QdrantClient(
            path="./qdrant_data"
        )

        self._ensure_collection()

    def _ensure_collection(self):

        collections = self.client.get_collections().collections
        existing = [c.name for c in collections]

        if self.collection_name not in existing:

            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=1536,
                    distance=Distance.COSINE
                )
            )

    def store_chunks(
        self,
        document_id: str,
        chunks: list[str],
        embeddings: list[list[float]]
    ):

        points = []

        for idx, (chunk, vector) in enumerate(zip(chunks, embeddings)):

            point = PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "document_id": document_id,
                    "chunk_index": idx,
                    "chunk_text": chunk
                }
            )

            points.append(point)

        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    def search(self, query_embedding: list[float], document_id: str, top_k=5):

        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=top_k,
            query_filter={
                "must": [
                    {
                        "key": "document_id",
                        "match": {
                            "value": document_id
                        }
                    }
                ]
            }
        )

        return results