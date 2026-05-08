from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os
from dotenv import load_dotenv

load_dotenv()
import joblib

app = FastAPI(
    title="Anomaly Detection API",
    description="MLOps-enabled API for Anomaly Detection",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

iqr_model = joblib.load(os.path.join(os.path.dirname(__file__), "..", "iqr_model.pkl"))
LOWER = iqr_model["LOWER"]
UPPER = iqr_model["UPPER"]


class AnomalyRequest(BaseModel):
    amount: float = Field(..., description="The amount to check for anomalies")


def classify_value(value, lower, upper):
    if lower <= value <= upper:
        return "Normal ✅"
    if value <= 0:
        return "Input Error ❌ (invalid value)"
    if value > upper * 3:
        return "Fraud Risk 🚨 (very unusual value)"
    return "Event / Unusual Spending ⚠️"


def predict_anomaly(amount):
    classification = classify_value(amount, LOWER, UPPER)
    return {
        "amount": amount,
        "lower_bound": LOWER,
        "upper_bound": UPPER,
        "classification": classification
    }


@app.get("/")
def root():
    return {"message": "Anomaly Detection API", "version": "1.0.0", "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/predict")
def predict_endpoint(req: AnomalyRequest):
    try:
        result = predict_anomaly(req.amount)
        return {"status": "success", "model": "anomaly_detection", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
