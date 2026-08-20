"""Spray event database model.

NOTE: servo_angle is a LEGACY database column retained to avoid risky
SQLite migrations.  It defaults to 0 and is NOT used by any active API,
controller, serial command, or UI path.  It will be removed in a future
schema migration when the project moves to a migration tool.
"""

from datetime import datetime
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SprayEvent(Base):
    __tablename__ = "spray_events"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    device_id: Mapped[int] = mapped_column(ForeignKey("devices.id"), nullable=True)
    detection_id: Mapped[int | None] = mapped_column(nullable=True)
    session_id: Mapped[int | None] = mapped_column(nullable=True)
    mode: Mapped[str] = mapped_column(String(20))  # auto/assisted/manual
    # LEGACY — retained to avoid SQLite migration; always 0 for new events.
    servo_angle: Mapped[int] = mapped_column(Integer, default=0)
    duration_ms: Mapped[int] = mapped_column(Integer)
    estimated_volume_ml: Mapped[float | None] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    command_id: Mapped[str | None] = mapped_column(String(50), unique=True, nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(200), nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
