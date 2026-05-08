from flask import Flask, render_template, request, jsonify
import requests
from dotenv import load_dotenv
import os
import sys
import subprocess
import threading
from pathlib import Path
from datetime import datetime

load_dotenv()

app = Flask(__name__)

API_URLS = {
    "scout_forecast": os.getenv("SCOUT_FORECAST_API_URL", "http://localhost:8001"),
    "annomalie":      os.getenv("ANNOMALIE_API_URL",      "http://localhost:8004"),
    "classification": os.getenv("CLASSIFICATION_API_URL", "http://localhost:8005"),
    "recommandation": os.getenv("RECOMMANDATION_API_URL", "http://localhost:8006"),
}

# ── Training pipeline definitions ──────────────────────────────────────────────
_ROOT = Path(__file__).resolve().parent.parent   # mlops/

PIPELINES = [
    {
        "id":   "scout_forecast",
        "name": "Scout Forecast",
        "dir":  str(_ROOT / "scout_forecast" / "scout_forecast"),
    },
    {
        "id":   "anomaly",
        "name": "Anomaly Detection",
        "dir":  str(_ROOT / "ML_Models" / "annomalie"),
    },
    {
        "id":   "classification",
        "name": "Retention Classification",
        "dir":  str(_ROOT / "ML_Models" / "classification"),
    },
    {
        "id":   "recommendation",
        "name": "Activity Recommendation",
        "dir":  str(_ROOT / "ML_Models" / "recommandation"),
    },
]

# ── Shared training state ───────────────────────────────────────────────────────
_train_lock  = threading.Lock()
_train_state = {
    "running":    False,
    "started_at": None,
    "models": {p["id"]: {"status": "idle", "message": ""} for p in PIPELINES},
}


def _run_training():
    """Background worker — runs each pipeline subprocess sequentially."""
    with _train_lock:
        _train_state["running"]    = True
        _train_state["started_at"] = datetime.now().isoformat()
        for p in PIPELINES:
            _train_state["models"][p["id"]] = {"status": "idle", "message": ""}

    for p in PIPELINES:
        with _train_lock:
            _train_state["models"][p["id"]]["status"]  = "running"
            _train_state["models"][p["id"]]["message"] = "Training…"

        try:
            result = subprocess.run(
                [sys.executable, "-m", "src.pipeline"],
                cwd=p["dir"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
            )
            if result.returncode == 0:
                status, msg = "done", "Completed successfully"
            else:
                lines = (result.stderr or result.stdout or "unknown error").strip().splitlines()
                status, msg = "error", " | ".join(lines[-3:])
        except Exception as exc:
            status, msg = "error", str(exc)

        with _train_lock:
            _train_state["models"][p["id"]]["status"]  = status
            _train_state["models"][p["id"]]["message"] = msg

    with _train_lock:
        _train_state["running"] = False


# ── Routes ──────────────────────────────────────────────────────────────────────

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/scout_forecast", methods=["GET", "POST"])
def scout_forecast():
    result = None
    if request.method == "POST":
        try:
            unit_id = request.form.get("unit_id")
            payload = {}
            if unit_id:
                payload["unit_id"] = int(unit_id)
            response = requests.post(f"{API_URLS['scout_forecast']}/predict/participation", json=payload)
            if response.status_code == 200:
                result = response.json()["result"]
        except Exception as e:
            result = {"error": str(e)}
    return render_template("scout_forecast.html", result=result)


@app.route("/annomalie", methods=["GET", "POST"])
def annomalie():
    result = None
    if request.method == "POST":
        try:
            amount = float(request.form["amount"])
            response = requests.post(f"{API_URLS['annomalie']}/predict", json={"amount": amount})
            if response.status_code == 200:
                result = response.json()["result"]
        except Exception as e:
            result = {"error": str(e)}
    return render_template("annomalie.html", result=result)


@app.route("/classification", methods=["GET", "POST"])
def classification():
    result = None
    if request.method == "POST":
        try:
            nb_members     = float(request.form["nb_members"])
            nb_leaders     = float(request.form["nb_leaders"])
            taux_evolution = float(request.form["taux_evolution"])
            response = requests.post(
                f"{API_URLS['classification']}/predict",
                json={"nb_members": nb_members, "nb_leaders": nb_leaders, "taux_evolution": taux_evolution},
            )
            if response.status_code == 200:
                result = response.json()["result"]
        except Exception as e:
            result = {"error": str(e)}
    return render_template("classification.html", result=result)


@app.route("/recommandation", methods=["GET", "POST"])
def recommandation():
    result = None
    if request.method == "POST":
        try:
            user_id  = int(request.form["user_id"])
            response = requests.post(f"{API_URLS['recommandation']}/predict", json={"user_id": user_id})
            if response.status_code == 200:
                result = response.json()["result"]
        except Exception as e:
            result = {"error": str(e)}
    return render_template("recommandation.html", result=result)


@app.route("/health/<int:port>")
def health_proxy(port: int):
    """Server-side proxy for service health checks — avoids browser CORS."""
    allowed = {5000, 8001, 8004, 8005, 8006}
    if port not in allowed:
        return jsonify({"error": "forbidden"}), 403
    try:
        r = requests.get(f"http://localhost:{port}/", timeout=2)
        return jsonify({"status": "up", "code": r.status_code}), 200
    except Exception:
        return jsonify({"status": "down"}), 503


@app.route("/train", methods=["POST"])
def train():
    """Kick off background retraining of all models."""
    with _train_lock:
        if _train_state["running"]:
            return jsonify({"error": "Training already in progress"}), 409
    threading.Thread(target=_run_training, daemon=True).start()
    return jsonify({"status": "started"}), 202


@app.route("/train/status")
def train_status():
    """Return current training state for all models."""
    with _train_lock:
        return jsonify(dict(_train_state))


if __name__ == "__main__":
    app.run(debug=True, port=5555)
