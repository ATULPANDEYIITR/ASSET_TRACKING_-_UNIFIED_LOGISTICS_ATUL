from datetime import datetime
from sqlalchemy import String, Text, DateTime, JSON, Integer, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.db.database import Base

class AutomationRule(Base):
    __tablename__ = "automation_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    event_type: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        index=True
    )

    condition: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    action: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    severity: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="info"
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True
    )

    execution_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    last_executed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
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
