.PHONY: help install train run-api run-app mlflow docker-build docker-up docker-down

help:
	@echo "Recommendation MLOps Project"
	@echo ""
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  train       - Run training pipeline"
	@echo "  run-api     - Start FastAPI server"
	@echo "  run-app     - Start Flask web app"
	@echo "  mlflow      - Start MLflow server"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-up   - Start Docker containers"
	@echo "  docker-down - Stop Docker containers"

install:
	pip install -r requirements.txt

train:
	cd src && python pipeline.py

run-api:
	uvicorn api.main:app --host 0.0.0.0 --port 8006 --reload

run-app:
	python recommandation.py

mlflow:
	mlflow server --host 0.0.0.0 --port 5000 --backend-store-uri sqlite:///mlflow.db --default-artifact-root ./mlartifacts

docker-build:
	docker-compose build

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down
