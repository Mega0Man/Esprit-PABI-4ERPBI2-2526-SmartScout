# Dockerfile for FastAPI
FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements_api.txt .

RUN pip install --no-cache-dir -r requirements_api.txt

COPY api/ ./api/
COPY src/ ./src/
COPY model.py ./model.py
COPY budget_model.py ./budget_model.py
COPY config.py ./config.py

EXPOSE 8000

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]