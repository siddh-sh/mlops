"""Train the car price model and save it with its metrics."""
import json
import os

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from src.features import CATEGORICAL, NUMERIC, TARGET, build_features

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(ROOT, "data", "car_data.csv")
MODEL_DIR = os.path.join(ROOT, "model")
MODEL_PATH = os.path.join(MODEL_DIR, "model.joblib")
METRICS_PATH = os.path.join(MODEL_DIR, "metrics.json")


MLFLOW_URI = os.getenv("MLFLOW_TRACKING_URI", f"sqlite:///{os.path.join(ROOT, 'mlflow.db')}")
EXPERIMENT = "car-price-prediction"
REGISTERED_MODEL = "car-price-model"


def build_pipeline(n_estimators: int = 150, max_depth: int = 14) -> Pipeline:
    pre = ColumnTransformer(
        [
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
            ("num", "passthrough", NUMERIC),
        ]
    )
    model = RandomForestRegressor(n_estimators=n_estimators, max_depth=max_depth, random_state=42, n_jobs=-1)
    return Pipeline([("pre", pre), ("model", model)])


def train(data_path: str = DATA_PATH, n_estimators: int = 150, max_depth: int = 14) -> dict:
    if not os.path.exists(data_path):
        from data.generate_data import generate

        generate().to_csv(data_path, index=False)

    df = pd.read_csv(data_path)
    X = build_features(df)
    # Log-transform the target: prices are heavily right-skewed.
    y = np.log1p(df[TARGET])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    pipe = build_pipeline(n_estimators, max_depth)
    pipe.fit(X_train, y_train)

    preds = np.expm1(pipe.predict(X_test))
    actual = np.expm1(y_test)
    metrics = {
        "r2": round(float(r2_score(actual, preds)), 4),
        "mae": round(float(mean_absolute_error(actual, preds)), 2),
        "n_train": int(len(X_train)),
        "n_test": int(len(X_test)),
    }

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(pipe, MODEL_PATH)
    with open(METRICS_PATH, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved model to {MODEL_PATH}: {metrics}")
    log_to_mlflow(pipe, X_train, {"n_estimators": n_estimators, "max_depth": max_depth,
                                  "test_size": 0.2, "n_rows": len(df)}, metrics)
    return metrics


def log_to_mlflow(pipe, X_sample, params: dict, metrics: dict) -> None:
    """Track the run in MLflow and register the model.

    Optional: the Docker image does not ship mlflow, so this is skipped there.
    """
    try:
        import mlflow
        import mlflow.sklearn
    except ImportError:
        return
    mlflow.set_tracking_uri(MLFLOW_URI)
    mlflow.set_experiment(EXPERIMENT)
    with mlflow.start_run():
        mlflow.log_params(params)
        mlflow.log_metrics({k: v for k, v in metrics.items() if k in ("r2", "mae")})
        mlflow.sklearn.log_model(
            pipe, "model", registered_model_name=REGISTERED_MODEL, input_example=X_sample.head(3)
        )


if __name__ == "__main__":
    train()
