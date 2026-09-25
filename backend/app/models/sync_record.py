from datetime import datetime

from sqlalchemy import String, Text, DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.database import Base


class SyncRecord(Base):

    __tablename__ = "sync_records"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    source_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True
    )

    source_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    records_found: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    records_created: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    records_updated: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    records_failed: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )
