from uuid import UUID
from pydantic import BaseModel

class QuizQuestion(BaseModel):
    quiz_id: UUID
    question: str

class UserSubmission(BaseModel):
    quiz_id: UUID
    user_answer: str

class VerificationTypeResponse(BaseModel):
    verification_type: str
    quiz_questions: list[QuizQuestion]

class QuizQuestionResponse(BaseModel):
    quiz_questions: list[QuizQuestion]

class QuizSubmitRequest(BaseModel):
    user_submission: list[UserSubmission]
    goal_id: UUID

class QuizSubmitResponse(BaseModel):
    result: str

class PresignRequest(BaseModel):
    verification_id: str
    content_type: str  # "image/jpeg"
    file_ext: str      # ".jpg" or ".png"

class PresignResponse(BaseModel):
    upload_url: str
    s3_key: str

class ConfirmRequest(BaseModel):
    verification_id: str
    s3_key: str
    meta: dict = {}

class PhotoViewResponse(BaseModel):
    verification_id: str
    view_url: str

class CreateVerificationResponse(BaseModel):
    verification_id: str

