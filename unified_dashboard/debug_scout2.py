import os, sys, traceback
sys.path.insert(0, r'C:\Users\mezen\Desktop\mlops\scout_forecast\scout_forecast')
from dotenv import load_dotenv
load_dotenv(r'C:\Users\mezen\Desktop\mlops\scout_forecast\scout_forecast\.env')

import warnings, numpy as np, pandas as pd
from sqlalchemy import create_engine
from statsmodels.tsa.arima.model import ARIMA

warnings.filterwarnings('ignore')
np.random.seed(42)

SYNTHETIC_SEASONS = 8

DB_URL = os.getenv("DB_URL", "postgresql+psycopg2://postgres:12345678@127.0.0.1:5432/New_DWw")
print("DB_URL:", DB_URL)

def get_engine(db_url):
    return create_engine(db_url)

def load_participation_data(engine):
    try:
        raw_conn = engine.raw_connection()
        try:
            df = pd.read_sql_query('SELECT * FROM "Fact_Participation_Activity";', raw_conn)
        finally:
            raw_conn.close()
        print("Loaded from DB")
    except Exception as e:
        print(f"DB failed ({e}), falling back to CSV...")
        csv_path = os.path.join(os.path.dirname(__file__), "..", "..", "ML_Models", "recommandation", "fact-participation.csv")
        print("CSV path:", os.path.abspath(csv_path))
        if os.path.exists(csv_path):
            df = pd.read_csv(csv_path)
            print("Loaded from CSV")
        else:
            print("CSV NOT FOUND!")
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

try:
    print("\n--- Running predict_participation() ---")
    engine = get_engine(DB_URL)
    unit_agg, global_agg, real_seasons = load_participation_data(engine)
    engine.dispose()
    print("real_seasons:", real_seasons)
    print("unit_agg empty?", unit_agg.empty)
    print("global_agg empty?", global_agg.empty)

    incomplete = detect_incomplete(global_agg)
    print("incomplete:", incomplete)

    data, all_seasons = generate_synthetic(unit_agg, real_seasons, SYNTHETIC_SEASONS, 'nb_participants')
    print("all_seasons:", all_seasons)

    working = data.copy()
    complete = [s for s in real_seasons if s != incomplete]
    ts = working[working['season'].isin(complete)].groupby('season_idx')['nb_participants'].sum().sort_index()
    print("ts length:", len(ts), "values:", ts.values)

    # ARIMA
    best_order = (1, 1, 1)
    fit = ARIMA(ts.values, order=best_order).fit()
    forecast = float(fit.forecast(1)[0])
    print("FORECAST:", forecast)

    history = {}
    for s in complete:
        val = working[working['season'] == s]['nb_participants'].sum()
        history[s] = int(val)
    last_val = list(history.values())[-1] if history else 1
    delta = round(((forecast - last_val) / (last_val + 1e-8)) * 100, 1)
    parts = real_seasons[-1].split('/')
    next_season = f"{int(parts[0])+1}/{int(parts[1])+1}"
    print("RESULT:", {"next_season": next_season, "forecast": round(forecast), "delta_percent": delta})

except Exception:
    traceback.print_exc()
