# src/train_participation.py
import os
import sys
import mlflow
import mlflow.statsmodels
import pandas as pd
import numpy as np
import warnings
from sqlalchemy import create_engine
from statsmodels.tsa.arima.model import ARIMA

warnings.filterwarnings('ignore')
np.random.seed(42)

# Avoid Windows `cp1252` stdout issues when MLflow prints unicode (e.g., emojis).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

SYNTHETIC_SEASONS = 8

def get_engine(db_url):
    return create_engine(db_url)

def load_data(engine):
    raw_conn = engine.raw_connection()
    try:
        df = pd.read_sql_query('SELECT * FROM "Fact_Participation_Activity";', raw_conn)
    finally:
        raw_conn.close()
    season_order = sorted(df['season'].unique())
    season_map = {s: i for i, s in enumerate(season_order)}
    df['season_idx'] = df['season'].map(season_map)

    unit_agg = (df.groupby(['id_unit', 'season', 'season_idx'])
                .agg(
                    nb_participants=('nb_participants', 'sum'),
                    nb_activities=('nb_activities', 'sum'),
                    avg_taux=('taux_participation', 'mean'),
                    avg_per_member=('avg_activities_per_member', 'mean'),
                    nb_activity_types=('id_activity', 'nunique'),
                    nb_geo=('id_geography', 'nunique'),
                    nb_records=('id_fact_activity', 'count'),
                ).reset_index().sort_values(['id_unit', 'season_idx']))

    global_agg = (df.groupby(['season', 'season_idx'])
                  .agg(nb_participants=('nb_participants', 'sum'),
                       nb_records=('id_fact_activity', 'count'))
                  .reset_index().sort_values('season_idx'))

    return unit_agg, global_agg, season_order, season_map

def detect_incomplete(global_agg):
    median_rec = global_agg['nb_records'].median()
    last = global_agg.iloc[-1]
    return last['season'] if last['nb_records'] < median_rec * 0.75 else None

def generate_synthetic(unit_agg, season_order, n_extra):
    units = sorted(unit_agg['id_unit'].unique())
    start_year = int(season_order[0].split('/')[0])
    syn_seasons = [f"{start_year-i}/{start_year-i+1}"
                   for i in range(n_extra, 0, -1)]

    rows = []
    for unit in units:
        u = unit_agg[unit_agg['id_unit'] == unit].sort_values('season_idx')
        mu_p = u['nb_participants'].mean()
        sd_p = max(u['nb_participants'].std(), mu_p * 0.08)
        mu_a = u['nb_activities'].mean()
        sd_a = max(u['nb_activities'].std(), mu_a * 0.08)
        mu_t = u['avg_taux'].mean()
        mu_m = u['avg_per_member'].mean()
        mu_ty = u['nb_activity_types'].mean()
        mu_g = u['nb_geo'].mean()

        for i, season in enumerate(syn_seasons):
            factor = 0.80 + (i / n_extra) * 0.18
            rows.append({
                'id_unit': unit,
                'season': season,
                'season_idx': -(n_extra - i),
                'nb_participants': max(1, round(np.random.normal(mu_p * factor, sd_p * 0.4))),
                'nb_activities': max(1, round(np.random.normal(mu_a * factor, sd_a * 0.4))),
                'avg_taux': float(np.clip(np.random.normal(mu_t, 5), 0, 100)),
                'avg_per_member': float(mu_m),
                'nb_activity_types': int(round(mu_ty)),
                'nb_geo': int(round(mu_g)),
                'nb_records': 1,
                'is_synthetic': True,
            })

    syn_df = pd.DataFrame(rows)
    unit_agg = unit_agg.copy()
    unit_agg['is_synthetic'] = False
    combined = pd.concat([syn_df, unit_agg], ignore_index=True)
    all_seasons = sorted(combined['season'].unique(), key=lambda s: int(s.split('/')[0]))
    new_map = {s: i for i, s in enumerate(all_seasons)}
    combined['season_idx'] = combined['season'].map(new_map)
    combined = combined.sort_values(['id_unit', 'season_idx']).reset_index(drop=True)
    return combined, all_seasons, new_map

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

def walk_forward_cv(ts_values, best_order):
    actuals, preds = [], []
    for end in range(4, len(ts_values)):
        train = ts_values[:end]
        try:
            fit = ARIMA(train, order=best_order).fit()
            pred = float(fit.forecast(1)[0])
            actuals.append(ts_values[end])
            preds.append(pred)
        except:
            pass
    return np.array(actuals), np.array(preds)

def compute_metrics(actuals, preds):
    mae = np.mean(np.abs(actuals - preds))
    rmse = np.sqrt(np.mean((actuals - preds) ** 2))
    mape = np.mean(np.abs((actuals - preds) / (np.abs(actuals) + 1e-8))) * 100
    return mae, rmse, mape

def train_participation(db_url, model_name="participation_model"):
    mlflow.set_experiment("scout_forecast_participation")

    with mlflow.start_run(
        run_name=f"run_{model_name}",
        nested=mlflow.active_run() is not None,
    ) as run:
        engine = get_engine(db_url)
        unit_agg, global_agg, real_seasons, season_map = load_data(engine)
        engine.dispose()

        mlflow.log_param("synthetic_seasons", SYNTHETIC_SEASONS)
        mlflow.log_param("n_real_seasons", len(real_seasons))

        incomplete_season = detect_incomplete(global_agg)
        mlflow.log_param("incomplete_season", incomplete_season)

        data, all_seasons, new_map = generate_synthetic(unit_agg, real_seasons, SYNTHETIC_SEASONS)
        complete_seasons = [s for s in real_seasons if s != incomplete_season]

        working_data = data.copy()
        ts = (working_data[working_data['season'].isin(complete_seasons)]
              .groupby('season_idx')['nb_participants'].sum().sort_index())

        best_order, best_aic = find_best_arima(ts.values)
        if best_order == (0, 1, 0):
            best_order = (1, 1, 0)

        mlflow.log_param("arima_order", str(best_order))
        mlflow.log_param("arima_aic", float(best_aic))

        actuals, preds = walk_forward_cv(ts.values, best_order)
        mae, rmse, mape = compute_metrics(actuals, preds)

        mlflow.log_metric("cv_mae", mae)
        mlflow.log_metric("cv_rmse", rmse)
        mlflow.log_metric("cv_mape", mape)

        fit_final = ARIMA(ts.values, order=best_order).fit()
        forecast = float(fit_final.forecast(1)[0])
        mlflow.log_metric("forecast_value", forecast)

        mlflow.statsmodels.log_model(fit_final, "arima_model")

        mlflow.log_metric("n_complete_seasons", len(complete_seasons))
        mlflow.log_metric("total_seasons", len(all_seasons))
        mlflow.log_metric("n_units", len(working_data['id_unit'].unique()))

        run_info = {
            "run_id": run.info.run_id,
            "arima_order": str(best_order),
            "cv_mae": round(mae, 2),
            "cv_rmse": round(rmse, 2),
            "cv_mape": round(mape, 2),
            "forecast": round(forecast),
        }
        print(f"Training complete: {run_info}")
        return run_info

if __name__ == "__main__":
    db_url = sys.argv[1] if len(sys.argv) > 1 else os.getenv("DB_URL")
    train_participation(db_url)
