import os
import sys
from datetime import datetime
import mlflow
from dotenv import load_dotenv

from pathlib import Path
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

try:
    from .train_recommendation import train_recommendation
except ImportError:
    from train_recommendation import train_recommendation


def run_pipeline(db_url=None):
    if db_url is None:
        db_url = os.getenv("DB_URL")
    if not db_url:
        raise ValueError(
            "Missing database URL. Pass `db_url` to `run_pipeline()` / CLI arg, "
            "or set the `DB_URL` environment variable."
        )

    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))
    
    try:
        mlflow.end_run()
    except Exception:
        pass
    
    experiment_name = "Activity_Recommendation"
    mlflow.set_experiment(experiment_name)

    print("=" * 60)
    print("RECOMMENDATION - AUTOMATED ML TRAINING PIPELINE")
    print("=" * 60)
    print(f"Timestamp   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"DB URL      : {db_url}")
    print(f"MLflow URI : {mlflow.get_tracking_uri()}")
    print("=" * 60)

    pipeline_run_name = f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    with mlflow.start_run(run_name=pipeline_run_name) as pipeline_run:
        mlflow.log_param("pipeline_start", datetime.now().isoformat())
        mlflow.log_param("db_url", db_url)

        print("\n[1/1] Training Recommendation Model...")
        print("-" * 60)
        recommendation_result = train_recommendation(db_url, "recommendation_v1")
        mlflow.log_param("recommendation_run_id", recommendation_result["run_id"])

        mlflow.log_param("pipeline_end", datetime.now().isoformat())

        print("\n" + "=" * 60)
        print("PIPELINE COMPLETE")
        print("=" * 60)
        print(f"Pipeline Run ID : {pipeline_run.info.run_id}")
        print(f"RMSE            : {recommendation_result['rmse']:.4f}")
        print(f"MAE             : {recommendation_result['mae']:.4f}")

    return {
        "pipeline_run_id": pipeline_run.info.run_id,
        "recommendation": recommendation_result,
    }


if __name__ == "__main__":
    db_url = sys.argv[1] if len(sys.argv) > 1 else None
    run_pipeline(db_url)
