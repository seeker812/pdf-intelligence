import os

from backend.app.api.v1.services.storage.base_storage import BaseStorageService


class LocalStorageService(BaseStorageService):

    def __init__(self):
        self.base_path = "uploaded_files"
        os.makedirs(self.base_path, exist_ok=True)

    def save_file(self, file, file_name: str) -> str:

        file_path = os.path.join(self.base_path, file_name)

        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        return file_path

    def delete_file(self, file_path: str) -> None:

        if os.path.exists(file_path):
            os.remove(file_path)
        else:
            raise FileNotFoundError(f"{file_path} does not exist")

    def get_file_url(self, file_path: str) -> str:
        """
        For local storage, this can return:
        - file path
        - or a URL if you expose static files later
        """

        return file_path
