from datetime import date as date_type
from datetime import datetime, timezone

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.enums import VisitStatus


class Visit(Base):
    __tablename__ = "visits"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    property_id: Mapped[int] = mapped_column(
        ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True
    )
    buyer_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    date: Mapped[date_type] = mapped_column(nullable=False)
    time_slot: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[VisitStatus] = mapped_column(
        Enum(VisitStatus, name="visit_status", values_callable=lambda e: [m.value for m in e]),
        default=VisitStatus.pending,
        nullable=False,
        index=True,
    )
    visitor_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    visitor_phone: Mapped[str | None] = mapped_column(String(30), nullable=True)
    note: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
