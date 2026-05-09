# api/main.py - FastAPI Model Serving
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
import os
import sys
from dotenv import load_dotenv

load_dotenv()
import warnings
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
from statsmodels.tsa.arima.model import ARIMA


warnings.filterwarnings('ignore')
np.random.seed(42)

SYNTHETIC_SEASONS = 8
MIN_TRAIN_ML = 10

UNIT_NAMES = {
    1: "الأشبال", 2: "الزهرات", 3: "الكشافة",
    4: "المرشدات", 5: "الجوالة", 6: "الدليلات", 7: "Unit 7"
}

app = FastAPI(
    title="Scout Forecast API",
    description="MLOps-enabled API for Scout Participation Forecasting",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_URL = os.getenv("DB_URL", "postgresql+psycopg2://postgres:12345678@127.0.0.1:5432/New_DWw")

class ParticipationRequest(BaseModel):
    unit_id: Optional[int] = Field(None, description="Unit ID (1-7). None for all units.")



def get_engine(db_url):
    return create_engine(db_url)

def load_participation_data(engine):
    # Try loading from database first, but fall back to project CSVs if it fails
    try:
        raw_conn = engine.raw_connection()
        try:
            df = pd.read_sql_query('SELECT * FROM "Fact_Participation_Activity";', raw_conn)
        finally:
            raw_conn.close()
    except Exception:
        # Silently fall back to CSV if DB fails
        csv_path = os.path.join(os.path.dirname(__file__), "..", "..", "ML_Models", "recommandation", "fact-participation.csv")
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
        else:
            # Last resort: return empty structure to avoid crash
            return pd.DataFrame(), pd.DataFrame(), []

    season_order = sorted(df['season'].unique())
    season_map = {s: i for i, s in enumerate(season_order)}
    df['season_idx'] = df['season'].map(season_map)
    unit_agg = (df.groupby(['id_unit', 'season', 'season_idx'])
                .agg(nb_participants=('nb_participants', 'sum'),
                     nb_activities=('nb_activities', 'sum'),
                     avg_taux=('taux_participation', 'mean'),
                     avg_per_member=('avg_activities_per_member', 'mean'),
                     nb_activity_types=('id_activity', 'nunique'),
                     nb_geo=('id_geography', 'nunique'),
                     nb_records=('id_fact_activity', 'count'))
                .reset_index().sort_values(['id_unit', 'season_idx']))
    global_agg = (df.groupby(['season', 'season_idx'])
                  .agg(nb_participants=('nb_participants', 'sum'),
                       nb_records=('id_fact_activity', 'count'))
                  .reset_index().sort_values('season_idx'))
    return unit_agg, global_agg, season_order



def detect_incomplete(global_agg):
    median_rec = global_agg['nb_records'].median()
    last = global_agg.iloc[-1]
    return last['season'] if last['nb_records'] < median_rec * 0.75 else None

def generate_synthetic(unit_agg, season_order, n_extra, target_col):
    units = sorted(unit_agg['id_unit'].unique())
    start_year = int(season_order[0].split('/')[0])
    syn_seasons = [f"{start_year-i}/{start_year-i+1}" for i in range(n_extra, 0, -1)]
    rows = []
    for unit in units:
        u = unit_agg[unit_agg['id_unit'] == unit].sort_values('season_idx')
        mu = u[target_col].mean()
        sd = max(u[target_col].std(), mu * 0.1)
        for i, season in enumerate(syn_seasons):
            factor = 0.8 + (i / n_extra) * 0.2
            row = {'id_unit': unit, 'season': season, 'season_idx': -(n_extra - i),
                   target_col: np.random.normal(mu * factor, sd * 0.4), 'nb_records': 1, 'is_synthetic': True}
            rows.append(row)
    syn_df = pd.DataFrame(rows)
    unit_agg = unit_agg.copy()
    unit_agg['is_synthetic'] = False
    combined = pd.concat([unit_agg, syn_df], ignore_index=True)
    all_seasons = sorted(combined['season'].unique(), key=lambda s: int(s.split('/')[0]))
    new_map = {s: i for i, s in enumerate(all_seasons)}
    combined['season_idx'] = combined['season'].map(new_map)
    combined = combined.sort_values(['id_unit', 'season_idx']).reset_index(drop=True)
    return combined, all_seasons

def find_best_arima(ts_values):
    best_aic, best_order = np.inf, (1, 1, 1)
    for p in range(0, 3):
        for d in range(0, 2):
            for q in range(0, 3):
                try:
                    fit = ARIMA(ts_values, order=(p, d, q)).fit()
                    if fit.aic < best_aic:
                        best_aic, best_order = fit.aic, (p, d, q)
                except:
                    continue
    return best_order, best_aic

def predict_participation(unit_id=None):
    engine = get_engine(DB_URL)
    unit_agg, global_agg, real_seasons = load_participation_data(engine)
    engine.dispose()

    incomplete = detect_incomplete(global_agg)
    data, all_seasons = generate_synthetic(unit_agg, real_seasons, SYNTHETIC_SEASONS, 'nb_participants')

    working = data.copy()
    if unit_id:
        working = working[working['id_unit'] == int(unit_id)]

    complete = [s for s in real_seasons if s != incomplete]
    ts = working[working['season'].isin(complete)].groupby('season_idx')['nb_participants'].sum().sort_index()

    best_order, best_aic = find_best_arima(ts.values)
    if best_order == (0, 1, 0):
        best_order = (1, 1, 0)

    fit = ARIMA(ts.values, order=best_order).fit()
    forecast = float(fit.forecast(1)[0])

    history = {}
    for s in complete:
        val = working[working['season'] == s]['nb_participants'].sum()
        history[s] = int(val)

    last_val = list(history.values())[-1] if history else 1
    delta = round(((forecast - last_val) / (last_val + 1e-8)) * 100, 1)

    parts = real_seasons[-1].split('/')
    next_season = f"{int(parts[0])+1}/{int(parts[1])+1}"

    label = UNIT_NAMES.get(int(unit_id), f"Unit {unit_id}") if unit_id else "All Units"

    return {
        "next_season": next_season,
        "forecast": round(forecast),
        "delta_percent": delta,
        "best_arima_order": str(best_order),
        "aic": round(best_aic, 2),
        "incomplete_season": incomplete,
        "history": {k: int(v) for k, v in history.items()},
        "unit_id": label,
    }



@app.get("/")
def root():
    return {"message": "Scout Forecast API", "version": "1.0.0", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/predict/participation")
def predict_participation_endpoint(req: ParticipationRequest):
    try:
        result = predict_participation(unit_id=req.unit_id)
        return {"status": "success", "model": "participation_forecast", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/predict")
def predict_all(req: ParticipationRequest):
    try:
        result = predict_participation(unit_id=req.unit_id)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)