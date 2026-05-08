# run_mlflow.sh / run_mlflow.bat
# Start MLflow tracking server
mlflow ui --backend-store-uri sqlite:///mlflow.db --host 0.0.0.0 --port 5000