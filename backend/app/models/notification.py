from datetime import datetime
from sqlalchemy import String, Text, DateTime, JSON, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.db.database import Base

class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    event_id: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
        index=True
    )

    notification_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="in_app"
    )

    title: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    severity: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="info",
        index=True
    )

    read: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True
    )

    read_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    notification_data: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
        index=True
    )
