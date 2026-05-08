import os
import mlflow
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from dotenv import load_dotenv
import joblib

load_dotenv()


def train_anomaly(db_url, model_name="anomaly_detection_v1"):
    try:
        mlflow.end_run()
    except Exception:
        pass
    
    experiment_name = "Anomaly_Detection"
    mlflow.set_experiment(experiment_name)
        
    print(f"Connecting to database: {db_url}")
    engine = create_engine(db_url)
    
    try:
        with engine.connect() as conn:
            df = pd.read_sql('SELECT * FROM "Fact_Budget";', conn)
    except Exception as e:
        print(f"Using synthetic data (could not load from DB: {e})")
        np.random.seed(42)
        df = pd.DataFrame({
            "amount": np.random.normal(1000, 200, 1000)
        })
    
    engine.dispose()
    
    if "amount" not in df.columns:
        df = pd.DataFrame({
            "amount": np.random.normal(1000, 200, 1000)
        })
    
    amounts = df["amount"].dropna()
    Q1 = amounts.quantile(0.25)
    Q3 = amounts.quantile(0.75)
    IQR = Q3 - Q1
    LOWER = Q1 - 1.5 * IQR
    UPPER = Q3 + 1.5 * IQR
    
    model_data = {
        "LOWER": float(LOWER),
        "UPPER": float(UPPER),
        "Q1": float(Q1),
        "Q3": float(Q3),
        "IQR": float(IQR)
    }
    
    with mlflow.start_run(run_name=model_name):
        mlflow.log_param("model_type", "IQR_anomaly_detection")
        mlflow.log_metric("lower_bound", float(LOWER))
        mlflow.log_metric("upper_bound", float(UPPER))
        mlflow.log_metric("Q1", float(Q1))
        mlflow.log_metric("Q3", float(Q3))
        mlflow.log_metric("IQR", float(IQR))
        
        temp_path = os.path.join(os.path.dirname(__file__), "..", "temp_iqr_model.pkl")
        joblib.dump(model_data, temp_path)
        mlflow.log_artifact(temp_path, "model")
        os.remove(temp_path)
        
        run_id = mlflow.active_run().info.run_id
        print(f"Model trained successfully! Run ID: {run_id}")
    
    joblib.dump(model_data, os.path.join(os.path.dirname(__file__), "..", "iqr_model.pkl"))
    
    return {
        "run_id": run_id,
        "lower_bound": LOWER,
        "upper_bound": UPPER,
        "Q1": Q1,
        "Q3": Q3,
        "IQR": IQR
    }


if __name__ == "__main__":
    db_url = os.getenv("DB_URL")
    train_anomaly(db_url)
