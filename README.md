# MLOps Platform — Scout Treasury

This is the unified MLOps platform for the Scout Treasury project. It includes all machine learning services, the MLflow tracking server, and the Unified Dashboard.

## 🚀 1. Setup Instructions for the Group

### Prerequisites
Make sure you have Python (3.10+) installed.

### Installation
Open a terminal in the `mlops` folder and install all the requirements for the sub-projects:

```powershell
# Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# Install requirements (you might need to install them per-service if you prefer)
pip install fastapi uvicorn flask requests pandas numpy scikit-learn statsmodels psycopg2-binary sqlalchemy python-dotenv mlflow pydantic
```
*(Note: Each service also has its own `requirements.txt` if you want to install them separately).*

---

## ⚙️ 2. Database Configuration (IMPORTANT)

Before running anything, **you must update the database URL** to match your local PostgreSQL setup (username, password, port, and database name).

Update the `DB_URL` line in these **four** files:

1. `scout_forecast/scout_forecast/.env`
2. `ML_Models/annomalie/.env`
3. `ML_Models/classification/.env`
4. `ML_Models/recommandation/.env`

Example format:
`DB_URL=postgresql+psycopg2://YOUR_USERNAME:YOUR_PASSWORD@127.0.0.1:5432/YOUR_DB_NAME`

---

## 🏃 3. Running the Platform

To start everything (MLflow, 4 FastAPIs, and the Dashboard), simply run:

```powershell
cd unified_dashboard
python run_all.py
```
*(Or double-click the `run_all.bat` script).*

The Unified Dashboard will open at: **http://localhost:5555**

---

## 🧠 4. Retraining the Models

If you need to retrain the models and log them to MLflow:
1. Make sure the services are running.
2. Open the Unified Dashboard (**http://localhost:5555**).
3. Click the **"Retrain All Models"** button at the top to train all 4 pipelines automatically.
4. View the results on the MLflow UI at: **http://localhost:5000**
