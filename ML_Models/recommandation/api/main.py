from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.decomposition import TruncatedSVD
from dotenv import load_dotenv
import joblib

load_dotenv()

app = FastAPI(
    title="Recommendation API",
    description="MLOps-enabled API for Activity Recommendations",
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


def load_data():
    engine = create_engine(DB_URL)
    try:
        dim_activity = pd.read_sql('SELECT * FROM "Dim_Activity";', engine)
        fact_participation = pd.read_sql('SELECT * FROM "Fact_Participation_Activity";', engine)
    except Exception as e:
        print(f"Using CSV data (could not load from DB: {e})")
        dim_activity = pd.read_csv(os.path.join(os.path.dirname(__file__), "..", "dim-activity.csv"))
        fact_participation = pd.read_csv(os.path.join(os.path.dirname(__file__), "..", "fact-participation.csv"))
    engine.dispose()
    return dim_activity, fact_participation


dim_activity, fact_participation = load_data()

ratings = fact_participation[["id_unit", "id_activity", "nb_participants"]].copy()
ratings.rename(columns={"id_unit": "user_id", "id_activity": "item_id", "nb_participants": "rating"}, inplace=True)
ratings = ratings[ratings["rating"] > 0]

user_item_matrix = ratings.pivot_table(index="user_id", columns="item_id", values="rating").fillna(0)

svd = TruncatedSVD(n_components=20, random_state=42)
latent_matrix = svd.fit_transform(user_item_matrix)
pred_matrix = np.dot(latent_matrix, svd.components_)


class RecommendationRequest(BaseModel):
    user_id: int = Field(..., description="User/Unit ID")


def get_recommendations(user_id, top_k=5):
    if user_id not in user_item_matrix.index:
        return {"error": "User not found"}
    
    user_index = user_item_matrix.index.get_loc(user_id)
    pred_scores = pred_matrix[user_index]
    
    recommendations = sorted(
        list(zip(user_item_matrix.columns, pred_scores)),
        key=lambda x: x[1],
        reverse=True
    )[:top_k]
    
    recs = []
    for act, score in recommendations:
        act_name = dim_activity.loc[dim_activity["id_activity"] == act, "activity_name_en"].values[0] if "activity_name_en" in dim_activity.columns else f"Activity {act}"
        recs.append({
            "activity_id": int(act),
            "activity_name": act_name,
            "score": float(score)
        })
    
    return {
        "user_id": user_id,
        "recommendations": recs
    }


@app.get("/")
def root():
    return {"message": "Recommendation API", "version": "1.0.0", "status": "running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/predict")
def predict_endpoint(req: RecommendationRequest):
    try:
        result = get_recommendations(req.user_id)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return {"status": "success", "model": "activity_recommendation", "result": result}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
