import uuid
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from src.helpers.db import Base


class BountyLedger(Base):
    __tablename__ = "bounty_ledger"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="SET NULL"), nullable=True)
    amount = Column(Integer, nullable=False)
    type = Column(
        String,
        CheckConstraint("type IN ('fund', 'hold', 'release', 'forfeit', 'refund')"),
        nullable=False,
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    user = relationship("User")
    goal = relationship("Goal")


class BountyTransaction(Base):
    __tablename__ = "bounty_transactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    amount = Column(Integer, nullable=False)
    direction = Column(
        String,
        CheckConstraint("direction IN ('deposit', 'withdrawal')"),
        nullable=False,
    )
    status = Column(
        String,
        CheckConstraint("status IN ('pending', 'succeeded', 'failed')"),
        nullable=False,
    )
    payment_intent_id = Column(String, nullable=True)
    charge_id = Column(String, nullable=True)
    transfer_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User")