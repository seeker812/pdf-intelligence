from abc import ABC, abstractmethod


class BaseStorageService(ABC):

    @abstractmethod
    def save_file(self, file, file_name: str) -> str:
        pass

    @abstractmethod
    def delete_file(self, file_path: str) -> None:
        pass

    @abstractmethod
    def get_file_url(self, file_path: str) -> str:
        pass
