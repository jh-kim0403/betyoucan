import uuid
from sqlalchemy import (
    Column,
    Integer,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from src.helpers.db import Base


class WeeklyPoolDistribution(Base):
    __tablename__ = "weekly_pool_distributions"
    __table_args__ = (
        UniqueConstraint("week_start", "week_end", name="uq_weekly_pool_distribution_window"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    week_start = Column(DateTime(timezone=True), nullable=False)
    week_end = Column(DateTime(timezone=True), nullable=False)
    failed_pool_cents = Column(Integer, nullable=False, default=0)
    maintenance_fee_cents = Column(Integer, nullable=False, default=0)
    net_pool_cents = Column(Integer, nullable=False, default=0)
    distributed_total_cents = Column(Integer, nullable=False, default=0)
    successful_goals_count = Column(Integer, nullable=False, default=0)
    meta = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    items = relationship("WeeklyPoolDistributionItem", back_populates="distribution")


class WeeklyPoolDistributionItem(Base):
    __tablename__ = "weekly_pool_distribution_items"
    __table_args__ = (
        UniqueConstraint(
            "distribution_id", "goal_id", name="uq_weekly_pool_distribution_item_goal"
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    distribution_id = Column(
        UUID(as_uuid=True),
        ForeignKey("weekly_pool_distributions.id", ondelete="CASCADE"),
        nullable=False,
    )
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    goal_bounty_cents = Column(Integer, nullable=False)
    payout_cents = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    distribution = relationship("WeeklyPoolDistribution", back_populates="items")
