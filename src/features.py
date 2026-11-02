import pandas as pd

REFERENCE_YEAR = 2025
CATEGORICAL = ["brand", "fuel", "seller_type", "transmission", "owner"]
NUMERIC = ["car_age", "km_driven"]
TARGET = "selling_price"


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Turn raw CarDekho-style rows into model features."""
    out = pd.DataFrame()
    out["brand"] = df["name"].str.split().str[0]
    out["car_age"] = REFERENCE_YEAR - df["year"].astype(int)
    out["km_driven"] = df["km_driven"].astype(float)
    for col in ["fuel", "seller_type", "transmission", "owner"]:
        out[col] = df[col]
    return out[CATEGORICAL + NUMERIC]
