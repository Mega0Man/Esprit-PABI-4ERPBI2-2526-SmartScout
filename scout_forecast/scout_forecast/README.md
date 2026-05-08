# Scout Forecast - MLOps (PostgreSQL)

This project uses PostgreSQL + MLflow + FastAPI + Flask.

## Two DB Profiles (you and your friend)

You now have two environment profiles:

- `use_me_profile.bat` -> activates `.env.me` (`new_dw`, password `chtar`)
- `use_friend_profile.bat` -> activates `.env.friend` (original friend DB config)

Each script copies the selected profile to `.env`.

To generate two physical copies (`scout_forecast_me` and `scout_forecast_friend`) automatically:

```bash
.\make_scout_copies.bat
```

## Setup

```bash
pip install -r requirements.txt
```

If TLS certificate variables break pip on Windows:

```bash
set CURL_CA_BUNDLE=
set REQUESTS_CA_BUNDLE=
set SSL_CERT_FILE=
```

## Run Commands (PowerShell)

Use 4 terminals.

Terminal 0 (choose profile):

```bash
cd C:\Users\mezen\Desktop\mlops\scout_forecast\scout_forecast
.\use_me_profile.bat
```

Terminal 1 (MLflow):

```bash
cd C:\Users\mezen\Desktop\mlops\scout_forecast\scout_forecast
mlflow ui --backend-store-uri sqlite:///mlflow.db --host 0.0.0.0 --port 5000
```

Terminal 2 (training pipeline):

```bash
cd C:\Users\mezen\Desktop\mlops\scout_forecast\scout_forecast
python -m src.pipeline
```

Terminal 3 (FastAPI):

```bash
cd C:\Users\mezen\Desktop\mlops\scout_forecast\scout_forecast
uvicorn api.main:app --host 0.0.0.0 --port 8001
```

Terminal 4 (Flask web app):

```bash
cd C:\Users\mezen\Desktop\mlops\scout_forecast\scout_forecast
set API_URL=http://127.0.0.1:8001
set PORT=5001
python app.py
```

Open:

- MLflow: http://localhost:5000
- API docs: http://localhost:8001/docs
- Web app: http://localhost:5001

## API Endpoints

- `GET /`
- `GET /health`
- `POST /predict/participation`
- `POST /predict/budget`
- `POST /predict`

## Quick API Test

```bash
curl -X POST http://localhost:8001/predict/participation -H "Content-Type: application/json" -d "{\"unit_id\":1}"
curl -X POST http://localhost:8001/predict/budget -H "Content-Type: application/json" -d "{\"unit_id\":1}"
```