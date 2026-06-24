from types import TracebackType

from sqlalchemy.orm import Session

from app.infrastructure.database.session import SessionLocal


class UnitOfWork:
    def __init__(self, session: Session | None = None) -> None:
        self.session = session or SessionLocal()
        self._owns_session = session is None

    def __enter__(self) -> "UnitOfWork":
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc_type is not None:
            self.rollback()
        else:
            self.commit()

        if self._owns_session:
            self.session.close()

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()

