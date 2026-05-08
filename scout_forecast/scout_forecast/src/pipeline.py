# src/pipeline.py - Automated end-to-end training pipeline
import os
import sys
from datetime import datetime
import mlflow
from dotenv import load_dotenv

from pathlib import Path
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

# Avoid Windows `cp1252` stdout issues when MLflow prints unicode (e.g., emojis).
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Support both `python -m src.pipeline` (package execution) and
# `python src/pipeline.py` (direct script execution).
try:
    from .train_participation import train_participation
except ImportError:  # pragma: no cover
    from train_participation import train_participation

def run_pipeline(db_url=None):
    if db_url is None:
        db_url = os.getenv("DB_URL")
    if not db_url:
        raise ValueError(
            "Missing database URL. Pass `db_url` to `run_pipeline()` / CLI arg, "
            "or set the `DB_URL` environment variable."
        )

    mlflow.set_tracking_uri(os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000"))

    print("=" * 60)
    print("SCOUT FORECAST - AUTOMATED ML TRAINING PIPELINE")
    print("=" * 60)
    print(f"Timestamp   : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"DB URL      : {db_url}")
    print(f"MLflow URI  : {mlflow.get_tracking_uri()}")
    print("=" * 60)

    pipeline_run_name = f"pipeline_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    with mlflow.start_run(run_name=pipeline_run_name) as pipeline_run:
        mlflow.log_param("pipeline_start", datetime.now().isoformat())
        mlflow.log_param("db_url", db_url)

        print("\n[1/1] Training Participation Forecast Model...")
        print("-" * 60)
        participation_result = train_participation(db_url, "participation_v1")
        mlflow.log_param("participation_run_id", participation_result["run_id"])

        mlflow.log_param("pipeline_end", datetime.now().isoformat())

        print("\n" + "=" * 60)
        print("PIPELINE COMPLETE")
        print("=" * 60)
        print(f"Pipeline Run ID : {pipeline_run.info.run_id}")
        print(f"Participation   : {participation_result['cv_mae']:.2f} MAE | "
              f"{participation_result['cv_rmse']:.2f} RMSE")

    return {
        "pipeline_run_id": pipeline_run.info.run_id,
        "participation": participation_result,
    }

if __name__ == "__main__":
    db_url = sys.argv[1] if len(sys.argv) > 1 else None
    run_pipeline(db_url)
