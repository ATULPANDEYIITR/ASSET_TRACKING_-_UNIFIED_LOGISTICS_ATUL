from datetime import datetime
from sqlalchemy import String, Text, DateTime, JSON, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.db.database import Base

class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    event_type: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    message: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    severity: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="info",
        index=True
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="open",
        index=True
    )

    source: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True
    )

    asset_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True
    )

    asset_code: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True
    )

    event_data: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    acknowledged: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    acknowledged_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    resolved: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
