import subprocess
import sys
import os
import time
import signal
import requests
from threading import Thread

# ── Tracked processes for clean shutdown ──────────────────────────────────────
_processes: list[subprocess.Popen] = []

from pathlib import Path
_ROOT = Path(__file__).resolve().parent.parent

SERVICES = [
    {
        "name": "MLflow Server",
        "port": 5001,
        "dir": str(_ROOT / "mlflow"),
        "cmd": [
            "mlflow", "server",
            "--host", "0.0.0.0",
            "--port", "5001",
            "--backend-store-uri", "sqlite:///mlflow.db",
            "--default-artifact-root", "./mlartifacts",
        ],
    },
    {
        "name": "Scout Forecast FastAPI",
        "port": 8001,
        "dir": str(_ROOT / "scout_forecast" / "scout_forecast"),
        "cmd": ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8001"],
    },
    {
        "name": "Scout Forecast Flask",
        "port": 5000,
        "dir": str(_ROOT / "scout_forecast" / "scout_forecast"),
        "cmd": ["python", "app.py"],
    },
    {
        "name": "Anomaly Detection FastAPI",
        "port": 8004,
        "dir": str(_ROOT / "ML_Models" / "annomalie"),
        "cmd": ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8004"],
    },
    {
        "name": "Anomaly Detection Flask",
        "port": 5004,
        "dir": str(_ROOT / "ML_Models" / "annomalie"),
        "cmd": ["python", "appanomalie.py"],
    },
    {
        "name": "Classification FastAPI",
        "port": 8005,
        "dir": str(_ROOT / "ML_Models" / "classification"),
        "cmd": ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8005"],
    },
    {
        "name": "Classification Flask",
        "port": 5002,
        "dir": str(_ROOT / "ML_Models" / "classification"),
        "cmd": ["python", "app.py"],
    },
    {
        "name": "Recommendation FastAPI",
        "port": 8006,
        "dir": str(_ROOT / "ML_Models" / "recommandation"),
        "cmd": ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8006"],
    },
    {
        "name": "Recommendation Flask",
        "port": 5003,
        "dir": str(_ROOT / "ML_Models" / "recommandation"),
        "cmd": ["python", "recommandation.py"],
    },
    {
        "name": "Unified Dashboard",
        "port": 5555,
        "dir": str(_ROOT / "unified_dashboard"),
        "cmd": ["python", "app.py"],
    },
]

STARTUP_DELAY   = 2   # seconds between each service launch
MLFLOW_DELAY    = 4   # extra wait after MLflow (needs longer to init)
HEALTH_TIMEOUT  = 15  # seconds to wait for health check


def launch_service(service: dict) -> subprocess.Popen:
    """Start a service subprocess with its own working directory (thread-safe)."""
    return subprocess.Popen(
        service["cmd"],
        cwd=service["dir"],          # ← cwd per-process, NOT os.chdir()
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )


def stream_logs(proc: subprocess.Popen, label: str) -> None:
    """Forward a process's stdout to the console with a service prefix."""
    try:
        for line in proc.stdout:
            print(f"[{label}] {line}", end="")
    except ValueError:
        pass  # pipe closed on shutdown


def health_check(port: int, timeout: int = HEALTH_TIMEOUT) -> bool:
    """Poll http://localhost:<port>/ until it responds or times out."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            r = requests.get(f"http://localhost:{port}/", timeout=1)
            if r.status_code < 500:
                return True
        except requests.exceptions.ConnectionError:
            pass
        time.sleep(1)
    return False


def shutdown(signum=None, frame=None) -> None:
    """Terminate all child processes gracefully."""
    print("\n\n⛔  Stopping all services…")
    for proc in _processes:
        try:
            proc.terminate()
        except Exception:
            pass
    # Give them a moment, then hard-kill stragglers
    time.sleep(2)
    for proc in _processes:
        try:
            proc.kill()
        except Exception:
            pass
    print("✅  All services stopped. Bye!")
    sys.exit(0)


def main() -> None:
    signal.signal(signal.SIGINT,  shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    print("=" * 60)
    print("  🚀  MLOps — Starting all services")
    print("=" * 60)

    for svc in SERVICES:
        print(f"\n▶  {svc['name']}  (port {svc['port']})")

        # Validate working directory exists before spawning
        if not os.path.isdir(svc["dir"]):
            print(f"   ⚠️  Directory not found, skipping: {svc['dir']}")
            continue

        proc = launch_service(svc)
        _processes.append(proc)

        # Stream logs in a background daemon thread
        log_thread = Thread(
            target=stream_logs,
            args=(proc, svc["name"][:6]),
            daemon=True,
        )
        log_thread.start()

        # MLflow needs a bit more time to initialise before other services connect
        delay = MLFLOW_DELAY if svc["port"] == 5000 else STARTUP_DELAY
        time.sleep(delay)

    # ── Health-check summary ─────────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("  📋  Health Check")
    print("=" * 60)
    all_ok = True
    for svc in SERVICES:
        ok = health_check(svc["port"])
        status = "✅  UP" if ok else "❌  DOWN (still starting?)"
        print(f"   {status}  —  {svc['name']:30s}  http://localhost:{svc['port']}")
        if not ok:
            all_ok = False

    print()
    if all_ok:
        print("🌐  All services healthy!  Open: http://localhost:5555")
    else:
        print("⚠️   Some services may still be loading — check the logs above.")
    print()
    print("Press CTRL+C to stop everything.\n")

    # ── Keep alive ───────────────────────────────────────────────────────────
    while True:
        # Restart any crashed process automatically
        for i, (svc, proc) in enumerate(zip(SERVICES, _processes)):
            if proc.poll() is not None:          # process exited
                print(f"\n⚠️  {svc['name']} crashed (exit {proc.returncode}). Restarting…")
                new_proc = launch_service(svc)
                _processes[i] = new_proc
                Thread(
                    target=stream_logs,
                    args=(new_proc, svc["name"][:6]),
                    daemon=True,
                ).start()
        time.sleep(5)


if __name__ == "__main__":
    main()
