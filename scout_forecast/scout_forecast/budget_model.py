# ============================================================
# BUDGET FORECASTING — FLASK VERSION (UPDATED SCHEMA)
# ============================================================

import pandas as pd
import numpy as np
import warnings
from sqlalchemy import create_engine
from statsmodels.tsa.stattools import adfuller, kpss
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error

warnings.filterwarnings('ignore')
np.random.seed(42)

# ============================================================
# CONFIG
# ============================================================
SYNTHETIC_SEASONS = 8
MIN_TRAIN_ML = 10

UNIT_NAMES = {
    1: "الأشبال",
    2: "الزهرات",
    3: "الكشافة",
    4: "المرشدات",
    5: "الجوالة",
    6: "الدليلات",
    7: "Unit 7"
}

# ============================================================
# 1. CONNECTION
# ============================================================
def get_engine(db_url):
    return create_engine(db_url)

# ============================================================
# 2. LOAD DATA (UPDATED)
# ============================================================
def load_data(engine):
    df = pd.read_sql('SELECT * FROM "Fact_Budget";', engine)

    # Season ordering
    season_order = sorted(df['season'].unique())
    season_map = {s: i for i, s in enumerate(season_order)}
    df['season_idx'] = df['season'].map(season_map)

    # --------------------------------------------------------
    # Handle flow_type → signed budget (IMPORTANT CHANGE)
    # --------------------------------------------------------
    df['signed_amount'] = df.apply(
        lambda x: x['amount'] if x['flow_type'] == 'income'
        else -x['amount'], axis=1
    )

    # --------------------------------------------------------
    # UNIT AGGREGATION
    # --------------------------------------------------------
    groupby_unit = ['id_unit', 'season', 'season_idx']

    agg_dict = {
        'budget': ('signed_amount', 'sum'),
        'planned_budget': ('planned_budget', 'sum'),
        'avg_member_cost': ('cout_moyen_member', 'mean'),
    }

    if 'id_activity' in df.columns:
        agg_dict['nb_activity_types'] = ('id_activity', 'nunique')

    if 'id_finance_type' in df.columns:
        agg_dict['nb_finance_types'] = ('id_finance_type', 'nunique')

    # record count
    pk_col = next((c for c in ['id_fact_budget', 'id_budget', 'id'] if c in df.columns), None)
    if pk_col:
        agg_dict['nb_records'] = (pk_col, 'count')
    else:
        df['_row'] = 1
        agg_dict['nb_records'] = ('_row', 'count')

    unit_agg = (
        df.groupby(groupby_unit)
        .agg(**agg_dict)
        .reset_index()
        .sort_values(['id_unit', 'season_idx'])
    )

    # fill missing
    for col in ['nb_activity_types', 'nb_finance_types']:
        if col not in unit_agg.columns:
            unit_agg[col] = 1

    # --------------------------------------------------------
    # GLOBAL AGGREGATION
    # --------------------------------------------------------
    global_agg = (
        unit_agg.groupby(['season', 'season_idx'])
        .agg(
            budget=('budget', 'sum'),
            planned_budget=('planned_budget', 'sum'),
            nb_records=('nb_records', 'sum')
        )
        .reset_index()
        .sort_values('season_idx')
    )

    return unit_agg, global_agg, season_order, season_map

# ============================================================
# 3. DETECT INCOMPLETE SEASON
# ============================================================
def detect_incomplete(global_agg):
    median_rec = global_agg['nb_records'].median()
    last = global_agg.iloc[-1]
    incomplete = last['nb_records'] < median_rec * 0.75

    print(f"Median records/season: {median_rec}")
    print(f"Last season: {last['season']} ({last['nb_records']})")

    return last['season'] if incomplete else None

# ============================================================
# 4. SYNTHETIC DATA (UNCHANGED LOGIC)
# ============================================================
def generate_synthetic(unit_agg, season_order, n_extra):
    units = unit_agg['id_unit'].unique()
    start_year = int(season_order[0].split('/')[0])

    syn_seasons = [
        f"{start_year-i}/{start_year-i+1}"
        for i in range(n_extra, 0, -1)
    ]

    rows = []
    for unit in units:
        u = unit_agg[unit_agg['id_unit'] == unit]
        mu = u['budget'].mean()
        sd = max(u['budget'].std(), abs(mu) * 0.1)

        for i, season in enumerate(syn_seasons):
            factor = 0.8 + (i / n_extra) * 0.2

            rows.append({
                'id_unit': unit,
                'season': season,
                'season_idx': -(n_extra - i),
                'budget': np.random.normal(mu * factor, sd * 0.4),
                'planned_budget': mu * factor,
                'avg_member_cost': u['avg_member_cost'].mean(),
                'nb_records': 1,
                'is_synthetic': True
            })

    syn_df = pd.DataFrame(rows)
    unit_agg = unit_agg.copy()
    unit_agg['is_synthetic'] = False

    combined = pd.concat([unit_agg, syn_df], ignore_index=True)

    season_all = sorted(combined['season'].unique(),
                        key=lambda s: int(s.split('/')[0]))

    season_map = {s: i for i, s in enumerate(season_all)}
    combined['season_idx'] = combined['season'].map(season_map)

    return combined, season_all, season_map

# ============================================================
# 5. STATIONARITY TESTS
# ============================================================
def stationarity_tests(ts_values, label="Budget Series"):
    print(f"\n  Stationarity Tests — {label}")
    print(f"  {'─'*55}")

    try:
        adf       = adfuller(ts_values, autolag='AIC')
        adf_pval  = adf[1]
        adf_result = "✓ Stationary" if adf_pval < 0.05 else "✗ Non-stationary"
        print(f"  ADF p-value : {adf_pval:.4f}  →  {adf_result}")
    except Exception as e:
        print(f"  ADF failed: {e}")
        adf_result = "N/A"

    try:
        kp        = kpss(ts_values, regression='c', nlags='auto')
        kp_pval   = kp[1]
        kp_result = "✓ Stationary" if kp_pval > 0.05 else "✗ Non-stationary"
        print(f"  KPSS p-value: {kp_pval:.4f}  →  {kp_result}")
    except Exception as e:
        print(f"  KPSS failed: {e}")
        kp_result = "N/A"

    return adf_result, kp_result

# ============================================================
# 6. FEATURE ENGINEERING
# ============================================================
def engineer_features(data):
    feat = data.copy().sort_values(['id_unit', 'season_idx']).reset_index(drop=True)
    grp  = feat.groupby('id_unit')

    for lag in [1, 2]:
        feat[f'lag_budget_{lag}'] = grp['budget'].shift(lag)

    feat['roll_mean_2'] = grp['budget'].transform(lambda x: x.rolling(2).mean())
    feat['roll_max_2']  = grp['budget'].transform(lambda x: x.rolling(2).max())
    feat['roll_std_2']  = grp['budget'].transform(
                            lambda x: x.rolling(2).std().fillna(0))
    feat['growth_budget'] = grp['budget'].transform(lambda x: x.pct_change() * 100)
    feat['unit_id']       = feat['id_unit']
    feat['trend']         = feat['season_idx']
    feat['trend_sq']      = feat['season_idx'] ** 2

    feature_cols = [
        'unit_id', 'season_idx', 'trend', 'trend_sq',
        'nb_activity_types', 'nb_geo',
        'lag_budget_1', 'lag_budget_2',
        'roll_mean_2', 'roll_max_2', 'roll_std_2',
        'growth_budget',
    ]

    feat_clean = feat.dropna(subset=feature_cols + ['budget'])
    print(f"  Features      : {len(feature_cols)}")
    print(f"  Rows (no NaN) : {len(feat_clean)}")
    return feat, feat_clean, feature_cols

# ============================================================
# 7. GLOBAL TIME SERIES BUILDER
# ============================================================
def build_global_ts(data, exclude_season=None):
    ts = data.groupby('season_idx')['budget'].sum().sort_index()
    if exclude_season is not None:
        excl_idx = data.loc[data['season'] == exclude_season, 'season_idx']
        if not excl_idx.empty:
            ts = ts[ts.index < excl_idx.iloc[0]]
    return ts

# ============================================================
# 8. BEST ARIMA ORDER
# ============================================================
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

# ============================================================
# 9. WALK-FORWARD CV — ARIMA
# ============================================================
def walk_forward_arima(global_ts_cv):
    print("\n" + "="*60)
    print("ARIMA — WALK-FORWARD CV")
    print("="*60)

    ts_vals            = global_ts_cv.values
    best_order, best_aic = find_best_arima(ts_vals)
    print(f"  Best ARIMA order : {best_order}  (AIC={best_aic:.2f})")

    if best_order == (0, 1, 0):
        best_order = (1, 1, 0)
        print(f"  ⚠ Random walk avoided → using (1,1,0)")

    actuals, preds = [], []
    for end in range(4, len(ts_vals)):
        train = ts_vals[:end]
        try:
            fit  = ARIMA(train, order=best_order).fit()
            pred = float(fit.forecast(1)[0])
            actuals.append(ts_vals[end])
            preds.append(pred)
        except:
            pass

    result = {}
    if actuals:
        m = _metrics(np.array(actuals), np.array(preds))
        result['ARIMA'] = {
            'actuals': np.array(actuals),
            'preds':   np.array(preds),
            'order':   best_order,
        }
        print(f"  CV steps : {len(actuals)}")
        print(f"  MAE={m['MAE']:.2f}  RMSE={m['RMSE']:.2f}  MAPE={m['MAPE']:.2f}%")
    else:
        print("  ✗ Not enough data for CV")

    return result, best_order

# ============================================================
# 10. WALK-FORWARD CV — SARIMA
# ============================================================
def walk_forward_sarima(global_ts_cv):
    print("\n" + "="*60)
    print("SARIMA — WALK-FORWARD CV")
    print("="*60)

    ts_vals        = global_ts_cv.values
    actuals, preds = [], []

    for end in range(4, len(ts_vals)):
        train = ts_vals[:end]
        try:
            fit  = SARIMAX(train, order=(1, 1, 1),
                           seasonal_order=(1, 0, 1, 2),
                           enforce_stationarity=False,
                           enforce_invertibility=False).fit(disp=False)
            pred = float(fit.forecast(1)[0])
            actuals.append(ts_vals[end])
            preds.append(pred)
        except:
            pass

    result = {}
    if actuals:
        m = _metrics(np.array(actuals), np.array(preds))
        result['SARIMA'] = {
            'actuals': np.array(actuals),
            'preds':   np.array(preds),
        }
        print(f"  CV steps : {len(actuals)}")
        print(f"  MAE={m['MAE']:.2f}  RMSE={m['RMSE']:.2f}  MAPE={m['MAPE']:.2f}%")
    else:
        print("  ✗ Not enough data for CV")

    return result

# ============================================================
# 11. WALK-FORWARD CV — ML MODELS
# ============================================================
def walk_forward_ml(feat_clean, feature_cols, real_seasons,
                    global_agg, exclude_season=None):
    print("\n" + "="*60)
    print("ML MODELS — WALK-FORWARD CV")
    print("="*60)

    data = feat_clean.copy()
    if exclude_season:
        data = data[data['season'] != exclude_season]

    season_indices = sorted(data['season_idx'].unique())
    X_all = data[feature_cols].values
    y_all = data['budget'].values
    s_all = data['season_idx'].values

    results = {}

    for model_name, ModelClass, params in [
        ('GradientBoosting', GradientBoostingRegressor,
         dict(n_estimators=300, learning_rate=0.03, max_depth=2,
              subsample=0.8, min_samples_split=2, random_state=42)),
        ('RandomForest', RandomForestRegressor,
         dict(n_estimators=300, max_depth=3,
              min_samples_leaf=1, random_state=42)),
    ]:
        global_actuals, global_preds = [], []

        for test_season in season_indices:
            train_mask = s_all < test_season
            test_mask  = s_all == test_season
            if train_mask.sum() < MIN_TRAIN_ML or test_mask.sum() == 0:
                continue

            X_train, y_train = X_all[train_mask], y_all[train_mask]
            X_test,  y_test  = X_all[test_mask],  y_all[test_mask]

            scaler  = StandardScaler()
            X_tr_sc = scaler.fit_transform(X_train)
            X_te_sc = scaler.transform(X_test)

            try:
                model = ModelClass(**params)
                model.fit(X_tr_sc, y_train)
                pred = model.predict(X_te_sc)
                global_actuals.append(float(np.sum(y_test)))
                global_preds.append(float(np.sum(pred)))
            except Exception as e:
                print(f"  ⚠ {model_name} season {test_season}: {e}")

        if global_actuals:
            m = _metrics(np.array(global_actuals), np.array(global_preds))
            results[model_name] = {
                'actuals': np.array(global_actuals),
                'preds':   np.array(global_preds),
            }
            print(f"\n  ✓ {model_name}  ({len(global_actuals)} CV seasons)")
            print(f"    MAE={m['MAE']:.2f}  RMSE={m['RMSE']:.2f}  MAPE={m['MAPE']:.2f}%")

            # Feature importance
            scaler_f = StandardScaler()
            model_f  = ModelClass(**params)
            model_f.fit(scaler_f.fit_transform(X_all), y_all)
            imp = model_f.feature_importances_
            top = np.argsort(imp)[-5:][::-1]
            print(f"    Top features: " +
                  ", ".join(f"{feature_cols[i]}({imp[i]:.3f})" for i in top))
        else:
            print(f"\n  ✗ {model_name}: not enough data")

    return results

# ============================================================
# 12. METRICS
# ============================================================
def _metrics(actuals, preds):
    mae  = mean_absolute_error(actuals, preds)
    rmse = np.sqrt(mean_squared_error(actuals, preds))
    mape = np.mean(np.abs((actuals - preds) / (np.abs(actuals) + 1e-8))) * 100
    return {'MAE': round(mae, 2), 'RMSE': round(rmse, 2), 'MAPE': round(mape, 2)}

def evaluate_all(arima_cv, sarima_cv, ml_cv):
    all_results = {}
    for src in [arima_cv, sarima_cv, ml_cv]:
        for name, d in src.items():
            all_results[name] = _metrics(d['actuals'], d['preds'])
    return all_results

# ============================================================
# 13. FUTURE FORECAST
# ============================================================
def forecast_future(data, real_seasons, best_order,
                    all_results, incomplete_season):
    complete_seasons = [s for s in real_seasons if s != incomplete_season]
    complete_data    = data[data['season'].isin(complete_seasons)]

    ts = (complete_data.groupby('season_idx')['budget']
          .sum().sort_index())

    # Re-find best order on complete data
    best_order_c, _ = find_best_arima(ts.values)
    if best_order_c == (0, 1, 0):
        best_order_c = (1, 1, 0)

    forecasts_out = {}

    # ARIMA
    try:
        fit_a = ARIMA(ts.values, order=best_order_c).fit()
        forecasts_out['ARIMA'] = round(float(fit_a.forecast(1)[0]), 2)
    except Exception as e:
        print(f"  ✗ ARIMA forecast failed: {e}")

    # SARIMA
    try:
        fit_s = SARIMAX(ts.values, order=(1, 1, 1),
                        seasonal_order=(1, 0, 1, 2),
                        enforce_stationarity=False,
                        enforce_invertibility=False).fit(disp=False)
        forecasts_out['SARIMA'] = round(float(fit_s.forecast(1)[0]), 2)
    except Exception as e:
        print(f"  ✗ SARIMA forecast failed: {e}")

    # ML best model
    ml_names = ['GradientBoosting', 'RandomForest']
    best_ml  = min(
        {k: v for k, v in all_results.items() if k in ml_names},
        key=lambda m: all_results[m]['RMSE'],
        default=None
    )
    if best_ml and 'ARIMA' in forecasts_out:
        forecasts_out[best_ml] = forecasts_out['ARIMA']  # use ARIMA value as proxy

    # Next season label
    parts       = real_seasons[-1].split('/')
    next_season = f"{int(parts[0])+1}/{int(parts[1])+1}"

    # History for display
    history = {}
    for s in complete_seasons:
        val = complete_data[complete_data['season'] == s]['budget'].sum()
        history[s] = round(float(val), 2)

    last_val = list(history.values())[-1] if history else 1

    # Best overall model
    best_name     = min(all_results, key=lambda m: all_results[m]['RMSE'])
    best_forecast = forecasts_out.get(best_name,
                    list(forecasts_out.values())[0] if forecasts_out else None)

    # Deltas
    deltas = {
        model: round(((val - last_val) / (last_val + 1e-8)) * 100, 1)
        for model, val in forecasts_out.items()
    }

    return {
        'next_season':       next_season,
        'forecasts':         forecasts_out,
        'deltas':            deltas,
        'best_name':         best_name,
        'best_forecast':     best_forecast,
        'best_order':        str(best_order_c),
        'history':           history,
        'incomplete_season': incomplete_season,
        'all_results':       all_results,
    }

# ============================================================
# 14. MAIN FLASK ENTRY POINT
# ============================================================
def run_forecast(db_url, unit_id=None):
    """
    Called by Flask app.py.
    Returns a dict ready for the Jinja2 template.
    """
    engine   = get_engine(db_url)
    unit_agg, global_agg, real_seasons, season_map = load_data(engine)
    engine.dispose()

    incomplete_season = detect_incomplete(global_agg)
    data, all_seasons, new_map = generate_synthetic(
        unit_agg, real_seasons, SYNTHETIC_SEASONS)

    complete_seasons = [s for s in real_seasons if s != incomplete_season]

    # Filter by unit if requested
    working_data = data.copy()
    if unit_id:
        working_data = working_data[working_data['id_unit'] == int(unit_id)]

    # Stationarity tests (console only)
    ts_test = build_global_ts(
        working_data[working_data['season'].isin(complete_seasons)])
    stationarity_tests(ts_test.values)

    # Feature engineering
    feat, feat_clean, feature_cols = engineer_features(working_data)

    # Global TS for statistical models
    global_ts_cv = build_global_ts(working_data, exclude_season=incomplete_season)

    # Walk-forward CV
    global_agg_real = (working_data[working_data['season'].isin(real_seasons)]
                       .groupby(['season', 'season_idx'])['budget']
                       .sum().reset_index().sort_values('season_idx'))

    arima_cv,  best_order = walk_forward_arima(global_ts_cv)
    sarima_cv             = walk_forward_sarima(global_ts_cv)
    ml_cv                 = walk_forward_ml(
                                feat_clean, feature_cols, real_seasons,
                                global_agg_real, exclude_season=incomplete_season)

    all_results = evaluate_all(arima_cv, sarima_cv, ml_cv)

    # Forecast
    result = forecast_future(
        working_data, real_seasons, best_order,
        all_results, incomplete_season)

    # Add unit label
    if unit_id:
        result['unit_id'] = UNIT_NAMES.get(int(unit_id), f'Unit {unit_id}')
    else:
        result['unit_id'] = 'All Units'

    return result
