from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, ConfigDict, model_validator
from typing import Any, Optional, Literal


class goalRequest(BaseModel):
    goal_type_id: UUID
    title: str
    user_input: str
    bounty_amount: int
    deadline: datetime
    notification_tone: Literal['harsh', 'normal', 'soft'] = 'harsh'

class goalResponse(BaseModel):
    id: UUID
    user_id: UUID
    goal_type_id: UUID
    title: str
    deadline: datetime
    created_at: datetime
    status: str
    quiz_question_status: Optional[str] = None
    verification_status: str
    goal_type: "goalTypeResponse"

    model_config = ConfigDict(from_attributes=True)

class goalTypeResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str] = None
    verification_type: str
    question_count: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)

class currentGoalResponse(BaseModel):
    id: UUID
    user_id: UUID
    goal_type_id: UUID
    title: str
    user_input: Optional[str] = None
    bounty_amount: int
    deadline: datetime
    status: str
    quiz_question_status: Optional[str] = None
    verification_status: str
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    goal_type_name: str
    verification_type: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

    @model_validator(mode="before")
    @classmethod
    def flatten_goal_type(cls, v: Any) -> Any:
        if hasattr(v, "goal_type") and v.goal_type is not None:
            obj = {col: getattr(v, col) for col in v.__table__.columns.keys()}
            obj["goal_type_name"] = v.goal_type.name
            obj["verification_type"] = v.goal_type.verification_type
            return obj
        return v

goalResponse.model_rebuild()
