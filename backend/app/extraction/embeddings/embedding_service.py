from langchain_openai import OpenAIEmbeddings


class EmbeddingService:
    """
    Handles generation of vector embeddings for document chunks.
    """

    def __init__(self):

        self.embedding_model = OpenAIEmbeddings(
            model="text-embedding-3-small"
        )

    def embed_chunks(self, chunks: list[str]) -> list[list[float]]:
        """
        Generate embeddings for list of text chunks.
        """

        embeddings = self.embedding_model.embed_documents(chunks)

        return embeddings

    def embed_query(self, query: str) -> list[float]:
        """
        Generate embedding for user query.
        """

        return self.embedding_model.embed_query(query)