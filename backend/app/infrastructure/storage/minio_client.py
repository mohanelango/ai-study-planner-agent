from typing import BinaryIO

from minio import Minio
from minio.error import S3Error

from app.core.config.settings import settings
from app.infrastructure.storage.base import StorageClient
from app.infrastructure.storage.exceptions import StorageConfigurationError, StorageDeleteError, StorageDownloadError, StorageUploadError


class MinIOStorageClient(StorageClient):
    def __init__(self) -> None:
        if not settings.MINIO_ENDPOINT or not settings.MINIO_ACCESS_KEY or not settings.MINIO_SECRET_KEY:
            raise StorageConfigurationError("MinIO settings are incomplete")
        self.client = Minio(
            endpoint=settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        self.default_bucket = settings.MINIO_BUCKET

    def ensure_bucket_exists(self, bucket_name: str | None = None) -> None:
        bucket = bucket_name or self.default_bucket
        try:
            if not self.client.bucket_exists(bucket):
                self.client.make_bucket(bucket)
        except S3Error as exc:
            raise StorageConfigurationError("Could not ensure MinIO bucket exists") from exc

    def upload_file(self, bucket_name: str, object_name: str, data: BinaryIO, length: int, content_type: str) -> None:
        try:
            self.ensure_bucket_exists(bucket_name)
            self.client.put_object(bucket_name, object_name, data, length=length, content_type=content_type)
        except S3Error as exc:
            raise StorageUploadError() from exc

    def download_file(self, bucket_name: str, object_name: str) -> bytes:
        try:
            response = self.client.get_object(bucket_name, object_name)
            try:
                return response.read()
            finally:
                response.close()
                response.release_conn()
        except S3Error as exc:
            raise StorageDownloadError() from exc

    def delete_file(self, bucket_name: str, object_name: str) -> None:
        try:
            self.client.remove_object(bucket_name, object_name)
        except S3Error as exc:
            raise StorageDeleteError() from exc

