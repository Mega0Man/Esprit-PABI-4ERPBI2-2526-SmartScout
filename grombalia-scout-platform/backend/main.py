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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
REQUEST_COUNT = Counter(
    "api_requests_total",
    "Total number of API requests",
    ["method", "endpoint", "role"],
)
INFERENCE_TIME = Histogram(
    "api_inference_duration_seconds",
    "Time spent processing ML inference",
    ["model", "role"],
)
INFERENCE_COUNT = Counter(
    "api_inference_total",
    "Total number of ML inferences",
    ["model", "role"],
)


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/metrics/{role}")
async def role_metrics(role: str):
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/signup", response_model=UserSchema)
async def signup(
    username: str, role: str, db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(User.username == username).first()
    if existing_user:
        # If user exists, we just return it (or we could update role if needed)
        return existing_user
    
    # Create new user with default password 'password'
    from auth import get_password_hash
    new_user = User(
        username=username,
        role=role,
        password_hash=get_password_hash("password")
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
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return create_user_token(user)


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

    REQUEST_COUNT.labels("POST", "/ml/forecasting", current_user.role).inc()
    INFERENCE_COUNT.labels("forecasting", current_user.role).inc()

    with INFERENCE_TIME.labels("forecasting", current_user.role).time():
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

    REQUEST_COUNT.labels("POST", "/ml/classification", current_user.role).inc()
    INFERENCE_COUNT.labels("classification", current_user.role).inc()

    with INFERENCE_TIME.labels("classification", current_user.role).time():
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

    REQUEST_COUNT.labels("POST", "/ml/anomaly", current_user.role).inc()
    INFERENCE_COUNT.labels("anomaly", current_user.role).inc()

    with INFERENCE_TIME.labels("anomaly", current_user.role).time():
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

    REQUEST_COUNT.labels("POST", "/ml/recommendation", current_user.role).inc()
    INFERENCE_COUNT.labels("recommendation", current_user.role).inc()

    with INFERENCE_TIME.labels("recommendation", current_user.role).time():
        # Simulate prediction
        activities = [
            "Camping",
            "Hiking",
            "First Aid Training",
            "Community Service",
            "Nature Exploration",
            "Team Building",
        ]
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

    uvicorn.run(app, host="0.0.0.0", port=8090)
