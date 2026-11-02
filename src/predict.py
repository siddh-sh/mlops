import os

import joblib
import numpy as np
import pandas as pd

from src.features import build_features
from src.train import MODEL_PATH, train


def load_model(path: str = MODEL_PATH):
    # Train on first use so the app also works on Streamlit Cloud,
    # where no model artifact is shipped.
    if not os.path.exists(path):
        train()
    return joblib.load(path)


def predict_price(model, car: dict) -> float:
    features = build_features(pd.DataFrame([car]))
    return float(np.expm1(model.predict(features)[0]))
