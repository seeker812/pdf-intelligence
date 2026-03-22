from docling.document_converter import DocumentConverter


class DoclingParser:
    """
    Converts PDF documents into Markdown using IBM Docling.
    """

    def __init__(self):
        self.converter = DocumentConverter()

    def parse(self, file_path: str) -> str:
        """
        Parse PDF file and return Markdown representation.
        """

        result = self.converter.convert(file_path)

        markdown_text = result.document.export_to_markdown()

        return markdown_text
