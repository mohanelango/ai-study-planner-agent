from abc import ABC, abstractmethod
from typing import BinaryIO


class StorageClient(ABC):
    @abstractmethod
    def ensure_bucket_exists(self, bucket_name: str | None = None) -> None:
        raise NotImplementedError

    @abstractmethod
    def upload_file(self, bucket_name: str, object_name: str, data: BinaryIO, length: int, content_type: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def download_file(self, bucket_name: str, object_name: str) -> bytes:
        raise NotImplementedError

    @abstractmethod
    def delete_file(self, bucket_name: str, object_name: str) -> None:
        raise NotImplementedError

