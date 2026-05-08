import os
import joblib
import pandas as pd
import numpy as np

MODEL_PATH = "random_forest_model.pkl"
SCALER_PATH = "scaler.pkl"
SELECTOR_PATH = "selector.pkl"

model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
selector = joblib.load(SELECTOR_PATH)

NB_MEMBERS_MEAN = 34.0
NB_MEMBERS_STD = 14.5
NB_LEADERS_MEAN = 4.1
NB_LEADERS_STD = 1.6


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


def predict(nb_members, nb_leaders, taux_evolution, season="2021/2022"):
    features = build_features(nb_members, nb_leaders, taux_evolution, season)
    prediction = model.predict(features)[0]
    proba = model.predict_proba(features)[0]
    
    label = "High Fidelity" if prediction == 1 else "Low Fidelity"
    confidence = round(float(max(proba)) * 100, 1)
    
    print(f"Input: nb_members={nb_members}, nb_leaders={nb_leaders}, taux_evolution={taux_evolution}")
    print(f"Prediction: {label} (Confidence: {confidence}%)")
    print()


print("Testing the model with different inputs...\n")

predict(45, 4, -4)
predict(0, 0, 0)
predict(80, 8, 20)
predict(10, 1, -20)
predict(50, 5, 10)

print("All tests done!")
