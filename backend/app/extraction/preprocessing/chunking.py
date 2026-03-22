from langchain_text_splitters import MarkdownHeaderTextSplitter


class ChunkingService:
    """
    Splits Markdown documents into semantic chunks.
    """

    def __init__(self):

        headers_to_split_on = [
            ("#", "Header1"),
            ("##", "Header2"),
            ("###", "Header3"),
        ]

        self.splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on,
            strip_headers=False,
        )

    def chunk(self, markdown_text: str):

        chunks = self.splitter.split_text(markdown_text)

        chunk_texts = [chunk.page_content for chunk in chunks]

        return chunk_texts
