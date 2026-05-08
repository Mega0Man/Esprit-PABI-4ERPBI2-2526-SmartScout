# tests/test_training.py
import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.train_participation import find_best_arima, generate_synthetic, detect_incomplete, compute_metrics
from src.train_budget import find_best_arima as find_best_arima_budget
import numpy as np
import pandas as pd

class TestParticipationTraining:
    def test_find_best_arima(self):
        ts = np.array([100, 110, 105, 115, 120, 118, 125, 130])
        order, aic = find_best_arima(ts)
        assert isinstance(order, tuple)
        assert len(order) == 3
        assert aic > 0

    def test_compute_metrics(self):
        actuals = np.array([100, 110, 105])
        preds = np.array([102, 108, 107])
        mae, rmse, mape = compute_metrics(actuals, preds)
        assert mae >= 0
        assert rmse >= 0
        assert mape >= 0

class TestDataProcessing:
    def test_generate_synthetic_shape(self):
        data = pd.DataFrame({
            'id_unit': [1, 1, 2, 2],
            'season': ['2020/2021', '2021/2022', '2020/2021', '2021/2022'],
            'season_idx': [0, 1, 0, 1],
            'nb_participants': [100, 110, 80, 90],
            'nb_activities': [10, 12, 8, 9],
            'avg_taux': [80, 82, 78, 80],
            'avg_per_member': [1.5, 1.6, 1.4, 1.5],
            'nb_activity_types': [3, 3, 2, 2],
            'nb_geo': [2, 2, 1, 1],
            'nb_records': [1, 1, 1, 1],
        })
        combined, all_seasons, new_map = generate_synthetic(data, ['2020/2021', '2021/2022'], 4, 'nb_participants')
        assert len(combined) > len(data)
        assert len(all_seasons) == 6

    def test_detect_incomplete(self):
        global_agg = pd.DataFrame({
            'season': ['2020/2021', '2021/2022', '2022/2023'],
            'season_idx': [0, 1, 2],
            'nb_records': [10, 10, 3]
        })
        result = detect_incomplete(global_agg)
        assert result == '2022/2023'

    def test_detect_incomplete_none(self):
        global_agg = pd.DataFrame({
            'season': ['2020/2021', '2021/2022', '2022/2023'],
            'season_idx': [0, 1, 2],
            'nb_records': [10, 10, 10]
        })
        result = detect_incomplete(global_agg)
        assert result is None