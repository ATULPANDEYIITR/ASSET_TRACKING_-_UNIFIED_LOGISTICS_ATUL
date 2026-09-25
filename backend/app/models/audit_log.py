from datetime import datetime

from sqlalchemy import String, Text, DateTime, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.database import Base


class AuditLog(Base):

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )

    entity_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    entity_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True
    )

    asset_code: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        index=True
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    old_data: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    new_data: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    source: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
