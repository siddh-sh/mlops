import os
import sys
import time

import streamlit as st
from prometheus_client import Counter, Gauge, Histogram, start_http_server

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.generate_data import BRANDS, FUELS, OWNERS, SELLERS, TRANSMISSIONS  # noqa: E402
from src.predict import load_model, predict_price  # noqa: E402

METRICS_PORT = int(os.getenv("METRICS_PORT", "8000"))


@st.cache_resource
def init_metrics():
    """Create metrics and start the /metrics endpoint once per process
    (Streamlit reruns this script on every interaction)."""
    metrics = {
        "requests": Counter("car_price_predictions_total", "Number of predictions", ["brand", "fuel"]),
        "errors": Counter("car_price_prediction_errors_total", "Number of failed predictions"),
        "latency": Histogram(
            "car_price_prediction_latency_seconds",
            "Prediction latency",
            buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1),
        ),
        "price": Histogram(
            "car_price_predicted_inr",
            "Distribution of predicted prices (INR)",
            buckets=(100_000, 250_000, 500_000, 1_000_000, 2_000_000, 5_000_000, 10_000_000),
        ),
        "last_price": Gauge("car_price_last_prediction_inr", "Most recent predicted price (INR)"),
    }
    try:
        start_http_server(METRICS_PORT)
    except OSError:
        pass  # port unavailable (e.g. Streamlit Cloud) - app still works
    return metrics


@st.cache_resource
def get_model():
    return load_model()


metrics = init_metrics()
model = get_model()

st.set_page_config(page_title="Car Price Predictor", page_icon="🚗")
st.title("🚗 Used Car Price Predictor")
st.caption("RandomForest model trained on CarDekho-style data · MLOps demo")

col1, col2 = st.columns(2)
with col1:
    brand = st.selectbox("Brand", list(BRANDS))
    car_model = st.selectbox("Model", BRANDS[brand][1])
    year = st.slider("Year", 2005, 2025, 2018)
    km_driven = st.number_input("Kilometers driven", 0, 500_000, 40_000, step=1_000)
with col2:
    fuel = st.selectbox("Fuel", list(FUELS))
    transmission = st.selectbox("Transmission", list(TRANSMISSIONS))
    seller_type = st.selectbox("Seller type", list(SELLERS))
    owner = st.selectbox("Owner", list(OWNERS))

if st.button("Predict price", type="primary"):
    car = {
        "name": f"{brand} {car_model}",
        "year": year,
        "km_driven": km_driven,
        "fuel": fuel,
        "seller_type": seller_type,
        "transmission": transmission,
        "owner": owner,
    }
    start = time.perf_counter()
    try:
        price = predict_price(model, car)
    except Exception as exc:
        metrics["errors"].inc()
        st.error(f"Prediction failed: {exc}")
    else:
        metrics["latency"].observe(time.perf_counter() - start)
        metrics["requests"].labels(brand=brand, fuel=fuel).inc()
        metrics["price"].observe(price)
        metrics["last_price"].set(price)
        st.success(f"Estimated price: ₹ {price:,.0f}")
