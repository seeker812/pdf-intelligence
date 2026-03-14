from pathlib import Path
import shutil
from uuid import uuid4

from fastapi import UploadFile

UPLOAD_DIR = Path(__file__).resolve().parents[2] / "temp_uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_uploaded_file(upload_file: UploadFile) -> str:
    file_name = Path(upload_file.filename or "upload.bin").name
    file_path = UPLOAD_DIR / f"{uuid4()}-{file_name}"

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    return str(file_path)
