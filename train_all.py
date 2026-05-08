"""
train_all.py — Retrain every MLOps model and log to the shared MLflow server.

Run AFTER starting the services (run_all.py / run_all.bat) so the
MLflow server at http://localhost:5000 is already up.

Usage:
    python train_all.py
"""
import sys
import os
import time
import subprocess
from pathlib import Path

# ── Colour helpers ────────────────────────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
RESET  = "\033[0m"
BOLD   = "\033[1m"

def ok(msg):   print(f"{GREEN}  ✅  {msg}{RESET}")
def warn(msg): print(f"{YELLOW}  ⚠️   {msg}{RESET}")
def err(msg):  print(f"{RED}  ❌  {msg}{RESET}")
def hdr(msg):  print(f"\n{BOLD}{msg}{RESET}")

# ── Pipeline definitions ──────────────────────────────────────
PIPELINES = [
    {
        "name":       "Scout Forecast (Participation)",
        "experiment": "scout_forecast_participation",
        "dir":        Path(__file__).parent / "scout_forecast" / "scout_forecast",
    },
    {
        "name":       "Anomaly Detection",
        "experiment": "Anomaly_Detection",
        "dir":        Path(__file__).parent / "ML_Models" / "annomalie",
    },
    {
        "name":       "Retention Classification",
        "experiment": "Retention_Classification",
        "dir":        Path(__file__).parent / "ML_Models" / "classification",
    },
    {
        "name":       "Activity Recommendation",
        "experiment": "Activity_Recommendation",
        "dir":        Path(__file__).parent / "ML_Models" / "recommandation",
    },
]

MLFLOW_URL = "http://localhost:5000"


def check_mlflow_running() -> bool:
    try:
        import requests
        r = requests.get(f"{MLFLOW_URL}/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def run_pipeline(svc: dict) -> bool:
    """Run `python -m src.pipeline` from the service's own directory."""
    svc_dir = svc["dir"].resolve()

    if not svc_dir.exists():
        err(f"Directory not found: {svc_dir}")
        return False

    result = subprocess.run(
        [sys.executable, "-m", "src.pipeline"],
        cwd=str(svc_dir),          # ← run from the service root so imports resolve
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return result.returncode == 0


def main():
    print("=" * 60)
    print(f"{BOLD}  🚀  MLOps — Train All Models{RESET}")
    print("=" * 60)
    print(f"  MLflow server : {MLFLOW_URL}")
    print()

    # ── Sanity check: MLflow must be running ──────────────────
    if not check_mlflow_running():
        err(f"MLflow server not reachable at {MLFLOW_URL}")
        warn("Start it first:  python unified_dashboard/run_all.py")
        sys.exit(1)
    ok("MLflow server is running\n")

    results = {}
    for i, svc in enumerate(PIPELINES, 1):
        hdr(f"[{i}/{len(PIPELINES)}]  {svc['name']}")
        print(f"  Experiment : {svc['experiment']}")
        print(f"  Directory  : {svc['dir']}")
        print("-" * 60)
        t0 = time.time()
        success = run_pipeline(svc)
        elapsed = time.time() - t0
        results[svc["name"]] = success
        if success:
            ok(f"Done in {elapsed:.1f}s")
        else:
            err("Training failed — check output above")

    # ── Summary ───────────────────────────────────────────────
    print("\n" + "=" * 60)
    print(f"{BOLD}  📋  Training Summary{RESET}")
    print("=" * 60)
    all_ok = True
    for name, success in results.items():
        status = f"{GREEN}PASS{RESET}" if success else f"{RED}FAIL{RESET}"
        print(f"  {status}  {name}")
        if not success:
            all_ok = False

    print()
    if all_ok:
        ok(f"All models trained!  View results → {MLFLOW_URL}")
    else:
        warn("Some pipelines failed. Check the logs above.")
    print()


if __name__ == "__main__":
    main()
