from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os
import numpy as np
import pandas as pd
from dotenv import load_dotenv
import joblib

load_dotenv()

app = FastAPI(
    title="Classification API",
    description="MLOps-enabled API for High Fidelity Classification",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "random_forest_model.pkl")
SCALER_PATH = os.path.join(os.path.dirname(__file__), "..", "scaler.pkl")
SELECTOR_PATH = os.path.join(os.path.dirname(__file__), "..", "selector.pkl")

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
selector = joblib.load(SELECTOR_PATH)

NB_MEMBERS_MEAN = 34.0
NB_MEMBERS_STD = 14.5
NB_LEADERS_MEAN = 4.1
NB_LEADERS_STD = 1.6


class ClassificationRequest(BaseModel):
    nb_members: float = Field(..., description="Number of members")
    nb_leaders: float = Field(..., description="Number of leaders")
    taux_evolution: float = Field(..., description="Evolution rate")
    season: str = Field("2021/2022", description="Season (e.g., '2021/2022')")


def build_features(nb_members, nb_leaders, taux_evolution, season="2021/2022"):
    ratio_leaders_members = nb_leaders / (nb_members + 1)
    
    if nb_members <= 20:
        size_category = 0
    elif nb_members <= 50:
        size_category = 1
    else:
        size_category = 2
    
    is_growing = 1 if taux_evolution > 0 else 0
    
    unit_strength = (
        (nb_members - NB_MEMBERS_MEAN) / NB_MEMBERS_STD +
        (nb_leaders - NB_LEADERS_MEAN) / NB_LEADERS_STD
    )
    
    season_encoded = 0
    if season == "2018/2019":
        season_encoded = 0
    elif season == "2019/2020":
        season_encoded = 1
    elif season == "2020/2021":
        season_encoded = 2
    elif season == "2021/2022":
        season_encoded = 3
    
    feature_cols = [
        'nb_members',
        'nb_leaders',
        'taux_evolution',
        'ratio_leaders_members',
        'size_category',
        'is_growing',
        'unit_strength',
        'season_encoded'
    ]
    
    features_dict = {
        'nb_members': nb_members,
        'nb_leaders': nb_leaders,
        'taux_evolution': taux_evolution,
        'ratio_leaders_members': ratio_leaders_members,
        'size_category': size_category,
        'is_growing': is_growing,
        'unit_strength': unit_strength,
        'season_encoded': season_encoded
    }
    
    X = pd.DataFrame([features_dict], columns=feature_cols)
    X_scaled = pd.DataFrame(scaler.transform(X), columns=feature_cols)
    X_selected = selector.transform(X_scaled)
    
    return X_selected


def predict_classification(nb_members, nb_leaders, taux_evolution, season="2021/2022"):
    features = build_features(nb_members, nb_leaders, taux_evolution, season)
    prediction = model.predict(features)[0]
    proba = model.predict_proba(features)[0]
    
    label = "High Fidelity 🟢" if prediction == 1 else "Low Fidelity 🔴"
    confidence = round(float(max(proba)) * 100, 1)
    
    return {
        "nb_members": nb_members,
        "nb_leaders": nb_leaders,
        "taux_evolution": taux_evolution,
        "season": season,
        "prediction": label,
        "prediction_class": int(prediction),
        "confidence": confidence
    }


@app.get("/")
def root():
    return {"message": "Classification API", "version": "1.0.0", "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/predict")
def predict_endpoint(req: ClassificationRequest):
    try:
        result = predict_classification(
            req.nb_members, 
            req.nb_leaders, 
            req.taux_evolution,
            req.season
        )
        return {"status": "success", "model": "high_fidelity_classification", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
