# Scout Forecast - MLOps Makefile

.PHONY: setup train mlflow api run clean help

help:
	@echo "Available commands:"
	@echo "  make setup      - Install dependencies"
	@echo "  make train      - Run the ML training pipeline"
	@echo "  make mlflow     - Start the MLflow tracking UI"
	@echo "  make api        - Start the FastAPI prediction server"
	@echo "  make run        - Start the Flask web application"
	@echo "  make clean      - Remove temporary files and logs"

setup:
	pip install -r requirements.txt

train:
	python -m src.pipeline

mlflow:
	mlflow ui --backend-store-uri sqlite:///mlflow.db --host 0.0.0.0 --port 5000

api:
	uvicorn api.main:app --host 0.0.0.0 --port 8001

run:
	@set API_URL=http://127.0.0.1:8001 && set PORT=5001 && python app.py

clean:
	rm -rf __pycache__ .pytest_cache
	rm -f error_log.txt
