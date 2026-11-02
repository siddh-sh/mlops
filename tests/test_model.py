import os

import pytest

from data.generate_data import generate
from src.predict import load_model, predict_price
from src.train import MODEL_PATH, train

SAMPLE_CAR = {
    "name": "Hyundai i20",
    "year": 2018,
    "km_driven": 40_000,
    "fuel": "Petrol",
    "seller_type": "Individual",
    "transmission": "Manual",
    "owner": "First Owner",
}


@pytest.fixture(scope="session")
def metrics():
    return train()


def test_dataset_schema():
    df = generate(n_rows=50)
    assert list(df.columns) == [
        "name", "year", "selling_price", "km_driven",
        "fuel", "seller_type", "transmission", "owner",
    ]
    assert (df["selling_price"] > 0).all()


def test_model_quality(metrics):
    assert os.path.exists(MODEL_PATH)
    assert metrics["r2"] > 0.8


def test_prediction_is_reasonable(metrics):
    price = predict_price(load_model(), SAMPLE_CAR)
    assert 50_000 < price < 2_000_000


def test_newer_car_costs_more(metrics):
    model = load_model()
    old = predict_price(model, {**SAMPLE_CAR, "year": 2008})
    new = predict_price(model, {**SAMPLE_CAR, "year": 2023})
    assert new > old
