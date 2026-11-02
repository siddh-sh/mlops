"""Run several training configurations so they can be compared in the MLflow UI."""
from src.train import train

CONFIGS = [
    {"n_estimators": 20, "max_depth": 4},
    {"n_estimators": 50, "max_depth": 8},
    {"n_estimators": 100, "max_depth": 12},
    {"n_estimators": 150, "max_depth": 14},
    {"n_estimators": 300, "max_depth": 20},
]

if __name__ == "__main__":
    for cfg in CONFIGS:
        print(cfg)
        train(**cfg)
