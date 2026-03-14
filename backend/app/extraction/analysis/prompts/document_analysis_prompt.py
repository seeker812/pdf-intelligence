def get_document_analysis_prompt(document_text: str):

    return f"""
You are an advanced document intelligence AI.

Analyze the following document and extract meaningful insights.

Return:

1. Short Summary (1 sentence)
2. Detailed Summary (3–5 sentences)
3. Main Topics discussed
4. Named Entities including:
   - people
   - organizations
   - locations
   - dates
   - monetary values
5. Important Sections with short descriptions.

Document:

{document_text}
"""