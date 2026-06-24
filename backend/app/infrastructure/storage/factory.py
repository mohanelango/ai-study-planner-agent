from app.infrastructure.storage.base import StorageClient
from app.infrastructure.storage.minio_client import MinIOStorageClient


def get_storage_client() -> StorageClient:
    return MinIOStorageClient()

