from pydantic import BaseModel, Field

class CreatePaymentIntentRequest(BaseModel):
    amount_cents: int = Field(..., gt=0)
    method: str  # "bank" | "card"

class CreatePaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str