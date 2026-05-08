# tests/test_api.py
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)

class TestAPI:
    def test_root(self):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "version" in data

    def test_health(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_predict_participation(self):
        response = client.post("/predict/participation", json={"unit_id": None})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "result" in data
        result = data["result"]
        assert "next_season" in result
        assert "forecast" in result
        assert "delta_percent" in result
        assert "best_arima_order" in result
        assert "history" in result

    def test_predict_participation_with_unit(self):
        response = client.post("/predict/participation", json={"unit_id": 1})
        assert response.status_code == 200
        data = response.json()
        result = data["result"]
        assert result["unit_id"] in ["الأشبال", "Unit 1"]

    def test_predict_budget(self):
        response = client.post("/predict/budget", json={"unit_id": None})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        result = data["result"]
        assert "next_season" in result
        assert "arima_forecast" in result
        assert "history" in result

    def test_predict_endpoint(self):
        response = client.post("/predict", json={"unit_id": None})
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "success"
        assert "result" in data