from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr

class UsersResponseModel(BaseModel):
  model_config = ConfigDict(from_attributes=True)
  first_name: str
  last_name: str
  email: EmailStr
  bounty_balance: int
