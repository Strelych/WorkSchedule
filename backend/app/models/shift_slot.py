from datetime import date, datetime, time
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Time
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class ShiftSlot(Base):
    __tablename__ = "shift_slots"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    period_id: Mapped[str] = mapped_column(String(36), ForeignKey("planning_periods.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    shift_type_id: Mapped[str] = mapped_column(String(64), nullable=False)
    role_required: Mapped[str] = mapped_column(String(32), nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    duration_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    max_people: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    current_people: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    is_overnight: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
