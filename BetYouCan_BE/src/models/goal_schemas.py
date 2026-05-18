import uuid
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    DateTime,
    ForeignKey,
    CheckConstraint,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from ..helpers.db import Base  # same Base used in user_schemas.py


class GoalType(Base):
    __tablename__ = "goal_types"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    description = Column(Text)
    verification_type = Column(
        String,
        CheckConstraint("verification_type IN ('photo','quiz')"),
        nullable=False,
    )
    question_count = Column(Integer, default=None)
    gpt_prompt = Column(Text)
    meta = Column(JSONB, server_default=text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    goals = relationship("Goal", back_populates="goal_type")


class Goal(Base):
    __tablename__ = "goals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    goal_type_id = Column(UUID(as_uuid=True), ForeignKey("goal_types.id"))
    title = Column(Text, nullable=False)
    user_input = Column(Text)
    bounty_amount = Column(Integer, CheckConstraint("bounty_amount >= 0"), nullable=False, default=0)
    deadline = Column(DateTime(timezone=True), nullable=False)
    notification_tone = Column(String, CheckConstraint("notification_tone IN ('harsh', 'normal', 'soft')"), server_default=text("'harsh'"), nullable=False)
    status = Column(
        String,
        CheckConstraint("status IN ('active', 'validating', 'resolved', 'canceled')"),
        server_default=text("'active'"),
        nullable=False,
    )
    quiz_question_status = Column(String, CheckConstraint("quiz_question_status IN ('pending', 'failed', 'created')"), default=None)
    verification_status = Column(String, CheckConstraint("verification_status IN ('not_started', 'completed', 'failed')"), server_default=text("'not_started'"), nullable=False)
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    goal_type = relationship("GoalType", back_populates="goals")
    # Optionally: user = relationship("User")  # if you want easy access to the owning user
