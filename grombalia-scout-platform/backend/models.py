from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MLInferenceLog(Base):
    __tablename__ = "ml_inference_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String, nullable=False)
    model_name = Column(String, nullable=False)
    input_data = Column(JSON)
    output_data = Column(JSON)
    inference_time_ms = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
