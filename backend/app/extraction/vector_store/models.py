from dataclasses import dataclass


@dataclass(frozen=True)
class ChunkPayload:

    document_id: str
    chunk_index: int
    chunk_text: str

    @classmethod
    def from_dict(cls, data: dict) -> "ChunkPayload":
        return cls(
            document_id=data["document_id"],
            chunk_index=data["chunk_index"],
            chunk_text=data["chunk_text"],
        )


@dataclass(frozen=True)
class SearchResult:

    chunk_text: str
    chunk_index: int
    document_id: str
    score: float
