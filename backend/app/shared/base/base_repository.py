from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from uuid import UUID

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    def add(self, entity: T) -> T:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, entity_id: UUID) -> T | None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, entity: T) -> None:
        raise NotImplementedError

