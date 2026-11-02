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


def build_pipeline() -> Pipeline:
    pre = ColumnTransformer(
        [
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
            ("num", "passthrough", NUMERIC),
        ]
    )
    model = RandomForestRegressor(n_estimators=150, max_depth=14, random_state=42, n_jobs=-1)
    return Pipeline([("pre", pre), ("model", model)])


def train(data_path: str = DATA_PATH) -> dict:
    if not os.path.exists(data_path):
        from data.generate_data import generate

        generate().to_csv(data_path, index=False)

    df = pd.read_csv(data_path)
    X = build_features(df)
    # Log-transform the target: prices are heavily right-skewed.
    y = np.log1p(df[TARGET])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    pipe = build_pipeline()
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
    return metrics


if __name__ == "__main__":
    train()
