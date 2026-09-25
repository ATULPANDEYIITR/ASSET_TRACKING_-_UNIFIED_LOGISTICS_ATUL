from datetime import datetime

from sqlalchemy import String, Text, Numeric, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column

from backend.app.db.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    asset_code: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    asset_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    serial_number: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
        index=True
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="active",
        index=True
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        index=True
    )

    owner: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    purchase_date: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    purchase_value: Mapped[float | None] = mapped_column(
        Numeric(15, 2),
        nullable=True
    )

    current_value: Mapped[float | None] = mapped_column(
        Numeric(15, 2),
        nullable=True
    )

    asset_metadata: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
