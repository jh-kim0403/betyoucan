import uuid
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    DateTime,
    Interval,
    ForeignKey,
    CheckConstraint,
    Boolean,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from src.helpers.db import Base

class QuizQuestions(Base):
    __tablename__ = "quiz_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True),server_default=func.now(),nullable=False)

    goal = relationship("Goal")

class QuizUserInput(Base):
    __tablename__ = "quiz_responses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    verification_id = Column(UUID(as_uuid=True), ForeignKey("verifications.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(UUID(as_uuid=True), ForeignKey("quiz_questions.id"), nullable=False)
    user_answer = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    verification = relationship("Verification")
    question = relationship("QuizQuestions")


class Verification(Base):
    __tablename__ = "verifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    verification_type = Column(String, CheckConstraint("verification_type IN ('photo', 'quiz')"), nullable=False)
    result = Column(
        String,
        CheckConstraint("result IN ('pending', 'completed', 'failed')"),
        nullable=False,
        server_default=text("'pending'"),
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    goal = relationship("Goal")
    photo = relationship("VerificationPhoto", back_populates="verification", uselist=False)


class VerificationPhoto(Base):
    __tablename__ = "verification_photos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    verification_id = Column(UUID(as_uuid=True), ForeignKey("verifications.id", ondelete="CASCADE"), nullable=False, unique=True)
    image_url = Column(Text, nullable=False)
    s3_key = Column(Text, nullable=False)
    meta = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    verification = relationship("Verification", back_populates="photo")
    
