import os, sys
sys.path.insert(0, r'C:\Users\mezen\Desktop\mlops\scout_forecast\scout_forecast')
from dotenv import load_dotenv
load_dotenv(r'C:\Users\mezen\Desktop\mlops\scout_forecast\scout_forecast\.env')

db_url = os.getenv('DB_URL', 'postgresql+psycopg2://postgres:12345678@127.0.0.1:5432/New_DWw')
print('DB_URL:', db_url)

from sqlalchemy import create_engine
import pandas as pd

try:
    engine = create_engine(db_url)
    raw_conn = engine.raw_connection()
    df = pd.read_sql_query('SELECT * FROM "Fact_Participation_Activity" LIMIT 5;', raw_conn)
    raw_conn.close()
    engine.dispose()
    print('DB SUCCESS - columns:', df.columns.tolist())
    print(df.head(2).to_string())
except Exception as e:
    print('DB ERROR:', type(e).__name__, str(e))
    # Now test the CSV path
    csv_path = r'C:\Users\mezen\Desktop\mlops\ML_Models\recommandation\fact-participation.csv'
    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)
        print('CSV columns:', df.columns.tolist())
        # Try the aggregation
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
        print('unit_agg sample:')
        print(unit_agg.head(3).to_string())
        print('global_agg:')
        print(global_agg.to_string())
