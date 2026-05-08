.PHONY: help install run train clean

help:
	@echo "============================================================"
	@echo "              MLOps Platform - Scout Treasury                 "
	@echo "============================================================"
	@echo "Available commands:"
	@echo "  make install  - Install all required Python dependencies"
	@echo "  make run      - Start MLflow, 4 FastAPIs, and the Dashboard"
	@echo "  make train    - Retrain all 4 ML models and log to MLflow"
	@echo "  make clean    - Remove python caches and temporary files"

install:
	pip install fastapi uvicorn flask requests pandas numpy scikit-learn statsmodels psycopg2-binary sqlalchemy python-dotenv mlflow pydantic

run:
	cd unified_dashboard && python run_all.py

train:
	python train_all.py

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	@echo "Cleaned up cache files."
