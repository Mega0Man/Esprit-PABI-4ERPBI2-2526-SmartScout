import os
import mlflow
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from dotenv import load_dotenv
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import mean_squared_error, mean_absolute_error
import joblib

load_dotenv()


def train_recommendation(db_url, model_name="recommendation_v1"):
    try:
        mlflow.end_run()
    except Exception:
        pass
    
    experiment_name = "Activity_Recommendation"
    mlflow.set_experiment(experiment_name)
        
    print(f"Connecting to database: {db_url}")
    engine = create_engine(db_url)
    
    try:
        with engine.connect() as conn:
            dim_activity = pd.read_sql('SELECT * FROM "Dim_Activity";', conn)
            fact_participation = pd.read_sql('SELECT * FROM "Fact_Participation_Activity";', conn)
    except Exception as e:
        print(f"Using CSV data (could not load from DB: {e})")
        dim_activity = pd.read_csv(os.path.join(os.path.dirname(__file__), "..", "dim-activity.csv"))
        fact_participation = pd.read_csv(os.path.join(os.path.dirname(__file__), "..", "fact-participation.csv"))
    
    engine.dispose()
    
    ratings = fact_participation[["id_unit", "id_activity", "nb_participants"]].copy()
    ratings.rename(columns={"id_unit": "user_id", "id_activity": "item_id", "nb_participants": "rating"}, inplace=True)
    ratings = ratings[ratings["rating"] > 0]
    
    user_item_matrix = ratings.pivot_table(index="user_id", columns="item_id", values="rating").fillna(0)
    
    svd = TruncatedSVD(n_components=20, random_state=42)
    latent_matrix = svd.fit_transform(user_item_matrix)
    pred_matrix = np.dot(latent_matrix, svd.components_)
    
    mask = user_item_matrix.values > 0
    actual = user_item_matrix.values[mask]
    predicted = pred_matrix[mask]
    
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    mae = mean_absolute_error(actual, predicted)
    
    with mlflow.start_run(run_name=model_name):
        mlflow.log_param("model_type", "TruncatedSVD")
        mlflow.log_param("n_components", 20)
        mlflow.log_metric("rmse", float(rmse))
        mlflow.log_metric("mae", float(mae))
        
        temp_path = os.path.join(os.path.dirname(__file__), "..", "temp_recommendation_model.pkl")
        model_data = {
            "svd": svd,
            "user_item_matrix": user_item_matrix,
            "latent_matrix": latent_matrix,
            "pred_matrix": pred_matrix,
            "dim_activity": dim_activity
        }
        joblib.dump(model_data, temp_path)
        mlflow.log_artifact(temp_path, "model")
        os.remove(temp_path)
        
        run_id = mlflow.active_run().info.run_id
        print(f"Model trained successfully! Run ID: {run_id}")
    
    return {
        "run_id": run_id,
        "rmse": rmse,
        "mae": mae
    }


if __name__ == "__main__":
    db_url = os.getenv("DB_URL")
    train_recommendation(db_url)
