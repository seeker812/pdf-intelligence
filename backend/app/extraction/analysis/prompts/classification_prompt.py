def get_classification_prompt(document_text: str):

    return f"""
You are an expert document classification AI.

Analyze the following document and determine the document type.

Possible document types include:

Financial Document
Invoice
Receipt
Research Paper
Legal Contract
Meeting Notes
Technical Documentation
Resume
Report
Email
General Document

Document:

{document_text}
"""