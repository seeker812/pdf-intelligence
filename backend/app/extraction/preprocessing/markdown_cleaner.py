import re


class MarkdownCleaner:
    def clean(self, markdown_text: str) -> str:

        text = markdown_text

        # remove excessive whitespace
        text = re.sub(r"\n{3,}", "\n\n", text)

        # remove trailing spaces
        text = re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE)

        # normalize spaces
        text = re.sub(r"[ ]{2,}", " ", text)

        return text.strip()
