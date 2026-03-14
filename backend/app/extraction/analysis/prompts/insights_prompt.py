def get_insights_prompt(document_text: str):

    return f"""
You are a document intelligence assistant.

Extract the most important insights from the following document.

Return between 3 and 8 key insights.

Document:

{document_text}
"""