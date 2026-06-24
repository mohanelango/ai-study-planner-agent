from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CurrentUserContext:
    id: UUID
    email: str
    full_name: str | None
    is_active: bool
    is_verified: bool

