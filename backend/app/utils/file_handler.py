import os
from fastapi import UploadFile

from backend.app.core.enums.error_codes import ErrorCode
from backend.app.core.exceptions import BadRequestException


class FileHandler:

    ALLOWED_EXTENSIONS = {"pdf"}

    @classmethod
    def validate(cls, file: UploadFile) -> None:

        if not file.filename:
            raise BadRequestException(
                message="File name is missing",
            )

        _, ext = os.path.splitext(file.filename)

        if not ext:
            raise BadRequestException(
                message="File has no extension",
            )

        ext = ext.lstrip(".").lower()

        if ext not in cls.ALLOWED_EXTENSIONS:
            raise BadRequestException(
                message=f"Unsupported file type: {ext}",
            )

    @classmethod
    def generate_file_name(cls, original_name: str, document_id: str) -> str:

        _, ext = os.path.splitext(original_name)

        if not ext:
            raise BadRequestException(
                message="Invalid file extension",
            )
        if original_name:
            return original_name

        return f"{document_id}{ext.lower()}"
