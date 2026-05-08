# model.py
import pandas as pd
import numpy as np
import warnings
from sqlalchemy import create_engine
from statsmodels.tsa.arima.model import ARIMA

warnings.filterwarnings('ignore')
np.random.seed(42)

SYNTHETIC_SEASONS = 8

UNIT_NAMES = {
    1: "الأشبال",
    2: "الزهرات",
    3: "الكشافة",
    4: "المرشدات",
    5: "الجوالة",
    6: "الدليلات",
}

def get_engine(db_url):
    return create_engine(db_url)

def load_data(engine):
    df = pd.read_sql('SELECT * FROM "Fact_Participation_Activity";', engine)
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
    print(f"\n  Generating {n_extra} synthetic seasons...")

    units      = sorted(unit_agg['id_unit'].unique())
    start_year = int(season_order[0].split('/')[0])
    syn_seasons = [f"{start_year-i}/{start_year-i+1}"
                   for i in range(n_extra, 0, -1)]

    rows = []
    for unit in units:
        u = unit_agg[unit_agg['id_unit'] == unit].sort_values('season_idx')
        mu_p  = u['nb_participants'].mean()
        sd_p  = max(u['nb_participants'].std(), mu_p * 0.08)
        mu_a  = u['nb_activities'].mean()
        sd_a  = max(u['nb_activities'].std(), mu_a * 0.08)
        mu_t  = u['avg_taux'].mean()
        mu_m  = u['avg_per_member'].mean()
        mu_ty = u['nb_activity_types'].mean()
        mu_g  = u['nb_geo'].mean()

        for i, season in enumerate(syn_seasons):
            factor = 0.80 + (i / n_extra) * 0.18
            rows.append({
                'id_unit':           unit,
                'season':            season,
                'season_idx':        -(n_extra - i),
                'nb_participants':   max(1, round(np.random.normal(mu_p * factor, sd_p * 0.4))),
                'nb_activities':     max(1, round(np.random.normal(mu_a * factor, sd_a * 0.4))),
                'avg_taux':          float(np.clip(np.random.normal(mu_t, 5), 0, 100)),
                'avg_per_member':    float(mu_m),
                'nb_activity_types': int(round(mu_ty)),
                'nb_geo':            int(round(mu_g)),
                'nb_records':        1,
                'is_synthetic':      True,
            })

    syn_df   = pd.DataFrame(rows)
    unit_agg = unit_agg.copy()
    unit_agg['is_synthetic'] = False

    combined    = pd.concat([syn_df, unit_agg], ignore_index=True)
    all_seasons = sorted(combined['season'].unique(),
                         key=lambda s: int(s.split('/')[0]))
    new_map     = {s: i for i, s in enumerate(all_seasons)}
    combined['season_idx'] = combined['season'].map(new_map)
    combined    = combined.sort_values(['id_unit', 'season_idx']).reset_index(drop=True)

    print(f"  ✓ {len(all_seasons)} total seasons "
          f"({n_extra} synthetic + {len(season_order)} real)")
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

def run_forecast(db_url, unit_id=None):
    """
    Main function called by Flask.
    Returns a dict with forecast results.
    """
    engine = get_engine(db_url)
    unit_agg, global_agg, real_seasons, season_map = load_data(engine)
    engine.dispose()

    incomplete_season = detect_incomplete(global_agg)
    data, all_seasons, new_map = generate_synthetic(unit_agg, real_seasons, SYNTHETIC_SEASONS)

    complete_seasons = [s for s in real_seasons if s != incomplete_season]

    # Filter by unit if requested
    working_data = data.copy()
    if unit_id:
        working_data = working_data[working_data['id_unit'] == int(unit_id)]

    ts = (working_data[working_data['season'].isin(complete_seasons)]
          .groupby('season_idx')['nb_participants']
          .sum().sort_index())

    best_order, best_aic = find_best_arima(ts.values)
    if best_order == (0, 1, 0):
        best_order = (1, 1, 0)

    # ARIMA forecast
    fit = ARIMA(ts.values, order=best_order).fit()
    arima_forecast = float(fit.forecast(1)[0])

    # Build history for display
    history = {}
    complete_data = working_data[working_data['season'].isin(complete_seasons)]
    for s in complete_seasons:
        val = complete_data[complete_data['season'] == s]['nb_participants'].sum()
        history[s] = int(val)

    last_val    = list(history.values())[-1] if history else 1
    parts       = real_seasons[-1].split('/')
    next_season = f"{int(parts[0])+1}/{int(parts[1])+1}"

    delta_arima = ((arima_forecast - last_val) / (last_val + 1e-8)) * 100

    # Resolve unit display name
    if unit_id:
        unit_label = UNIT_NAMES.get(int(unit_id), f'Unit {unit_id}')
    else:
        unit_label = 'All Units'

    return {
        'next_season':       next_season,
        'arima_forecast':    round(arima_forecast),
        'arima_delta':       round(delta_arima, 1),
        'best_order':        str(best_order),
        'incomplete_season': incomplete_season,
        'history':           history,
        'unit_id':           unit_label,
    }