from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import time
import random
import os
from dotenv import load_dotenv
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

from database import get_db
from models import User, MLInferenceLog
from schemas import (
    Token,
    User as UserSchema,
    UserCreate,
    ForecastingInput,
    ClassificationInput,
    AnomalyInput,
    RecommendationInput,
    PredictionResponse,
)
from auth import (
    authenticate_user,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    get_current_active_user,
)

load_dotenv()

app = FastAPI(title="Grombalia Scout Group API")

# Predefined list of valid IDs (Some are assigned to sample users in init_db.py)
VALID_IDS = [
    "12345678", "87654321", "11223344", "55667788", # Original list
    "99887766", "11112222", "33334444", "55556666", # Additional test IDs
    "12121212", "34343434", "56565656", "78787878",
    "00000000", "99999999"
]

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/metrics")
async def metrics():
    return {"status": "metrics disabled"}


@app.get("/metrics/{role}")
async def role_metrics(role: str):
    return {"status": "metrics disabled"}


@app.post("/signup", response_model=UserSchema)
async def signup(
    user_data: UserCreate, db: Session = Depends(get_db)
):
    # Check if ID is in the valid list
    if user_data.national_id not in VALID_IDS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid National ID. Please provide a verified 8-digit ID."
        )

    # Check if ID is already used
    existing_id = db.query(User).filter(User.national_id == user_data.national_id).first()
    if existing_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="National ID already registered."
        )

    # Check if username is unique
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken."
        )
    
    # Create new user
    from auth import get_password_hash
    new_user = User(
        username=user_data.username,
        role=user_data.role,
        national_id=user_data.national_id,
        password_hash=get_password_hash(user_data.password),
        face_descriptor=user_data.face_descriptor
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return create_user_token(user)


@app.post("/face-token", response_model=Token)
async def login_by_face(
    username: str, db: Session = Depends(get_db)
):
    print(f"Face login attempt for: {username}")
    user = db.query(User).filter(User.username == username).first()
    if not user:
        print(f"User {username} not found in database")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    print(f"User {username} found, creating token for role: {user.role}")
    return create_user_token(user)


@app.get("/face-descriptors")
async def get_face_descriptors(db: Session = Depends(get_db)):
    users = db.query(User).filter(User.face_descriptor != None).all()
    return {user.username: user.face_descriptor for user in users}


def create_user_token(user: User):
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=access_token_expires,
    )

    user_schema = UserSchema(
        id=user.id,
        username=user.username,
        role=user.role,
        created_at=user.created_at,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_schema,
    }


@app.get("/users/me", response_model=UserSchema)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


# --- ML Inference Endpoints ---

# Group Leader: Scout Forecasting
@app.post("/ml/forecasting", response_model=PredictionResponse)
async def forecasting(
    input: ForecastingInput,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "group_leader":
        raise HTTPException(status_code=403, detail="Not authorized")

    start_time = time.time()

    # Simulate prediction - in real setup, load from MLflow
    prediction = []
    for i in range(input.months):
        prediction.append(
            {
                "month": f"2025-{i+1:02d}",
                "predicted_scouts": random.randint(80, 120),
            }
        )

    inference_time = (time.time() - start_time) * 1000

    # Log inference
    log = MLInferenceLog(
        user_id=current_user.id,
        role=current_user.role,
        model_name="forecasting",
        input_data={"months": input.months},
        output_data={"prediction": prediction},
        inference_time_ms=inference_time,
    )
    db.add(log)
    db.commit()

    return {
        "model": "forecasting",
        "prediction": prediction,
        "inference_time_ms": inference_time,
    }


# Group Leader: Classification
@app.post("/ml/classification", response_model=PredictionResponse)
async def classification(
    input: ClassificationInput,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "group_leader":
        raise HTTPException(status_code=403, detail="Not authorized")

    start_time = time.time()

    # Simulate prediction
    classes = ["active", "inactive", "at_risk"]
    prediction = random.choice(classes)
    confidence = random.uniform(0.7, 0.98)

    inference_time = (time.time() - start_time) * 1000

    # Log inference
    log = MLInferenceLog(
        user_id=current_user.id,
        role=current_user.role,
        model_name="classification",
        input_data=input.dict(),
        output_data={"prediction": prediction, "confidence": confidence},
        inference_time_ms=inference_time,
    )
    db.add(log)
    db.commit()

    return {
        "model": "classification",
        "prediction": prediction,
        "confidence": confidence,
        "inference_time_ms": inference_time,
    }


# Treasurer: Anomaly Detection
@app.post("/ml/anomaly", response_model=PredictionResponse)
async def anomaly_detection(
    input: AnomalyInput,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "treasurer":
        raise HTTPException(status_code=403, detail="Not authorized")

    start_time = time.time()

    # Simulate prediction
    is_anomaly = random.random() > 0.9
    score = random.uniform(0, 1)

    inference_time = (time.time() - start_time) * 1000

    # Log inference
    log = MLInferenceLog(
        user_id=current_user.id,
        role=current_user.role,
        model_name="anomaly",
        input_data=input.dict(),
        output_data={"is_anomaly": is_anomaly, "score": score},
        inference_time_ms=inference_time,
    )
    db.add(log)
    db.commit()

    return {
        "model": "anomaly_detection",
        "prediction": {"is_anomaly": is_anomaly, "score": score},
        "inference_time_ms": inference_time,
    }


# Unit Leader: Recommendation System
@app.post("/ml/recommendation", response_model=PredictionResponse)
async def recommendation(
    input: RecommendationInput,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "unit_leader":
        raise HTTPException(status_code=403, detail="Not authorized")

    start_time = time.time()

    # Simulate prediction
    activities = ["hiking", "camping", "first_aid", "navigation", "cooking"]
    recommended_activities = random.sample(activities, k=3)

    inference_time = (time.time() - start_time) * 1000

    # Log inference
    log = MLInferenceLog(
        user_id=current_user.id,
        role=current_user.role,
        model_name="recommendation",
        input_data=input.dict(),
        output_data={"recommended_activities": recommended_activities},
        inference_time_ms=inference_time,
    )
    db.add(log)
    db.commit()

    return {
        "model": "recommendation_system",
        "prediction": recommended_activities,
        "inference_time_ms": inference_time,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8090, reload=True)
