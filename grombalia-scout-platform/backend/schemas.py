from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime


class UserBase(BaseModel):
    username: str
    role: str


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: User


class TokenData(BaseModel):
    username: Optional[str] = None


class ForecastingInput(BaseModel):
    months: int = 12


class ClassificationInput(BaseModel):
    age: int
    gender: str
    unit: str
    membership_years: int


class AnomalyInput(BaseModel):
    amount: float
    transaction_type: str
    category: str


class RecommendationInput(BaseModel):
    scout_id: int
    activity_preferences: list[str]


class PredictionResponse(BaseModel):
    model: str
    prediction: Any
    confidence: Optional[float] = None
    inference_time_ms: float
