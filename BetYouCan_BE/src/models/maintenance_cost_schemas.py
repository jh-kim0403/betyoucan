import uuid
from sqlalchemy import Column, Integer, DateTime, Text, UniqueConstraint, func, text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from src.helpers.db import Base


class WeeklyMaintenanceCost(Base):
    __tablename__ = "weekly_maintenance_costs"
    __table_args__ = (
        UniqueConstraint("week_start", "week_end", name="uq_weekly_maintenance_cost_window"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    week_start = Column(DateTime(timezone=True), nullable=False)
    week_end = Column(DateTime(timezone=True), nullable=False)
    aws_cost_cents = Column(Integer, nullable=False, default=0)
    openai_cost_cents = Column(Integer, nullable=False, default=0)
    fee_amount_cents = Column(Integer, nullable=False, default=0)
    source = Column(Text, nullable=False, default="automated")
    notes = Column(Text, nullable=True)
    meta = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
