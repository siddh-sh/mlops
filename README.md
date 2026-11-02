# Car Price Prediction – MLOps Project

Predicts used-car prices (RandomForest, CarDekho-style data) with a Streamlit UI, and ships it the MLOps way.

| Requirement | Where |
|---|---|
| GitHub version control | this repo |
| GitHub Actions CI/CD | `.github/workflows/ci-cd.yml` (lint → test → build/push image to GHCR → validate k8s) |
| Docker image | `Dockerfile`, `docker-compose.yml` |
| Kubernetes | `k8s/` (Deployment, Service, HPA, ServiceMonitor) |
| Terraform infra | `terraform/` (namespaces + kube-prometheus-stack via Helm) |
| Prometheus + Grafana | `monitoring/`, `k8s/servicemonitor.yaml` |
| Streamlit deploy | `app/streamlit_app.py` |

## Dataset
`data/generate_data.py` creates a synthetic dataset with the Kaggle *CarDekho* schema.
To use the real data, download it from Kaggle and save it as `data/car_data.csv`.

## Run locally
```bash
pip install -r requirements-dev.txt
python -m src.train          # trains model -> model/model.joblib
pytest -q
streamlit run app/streamlit_app.py
```

## Docker + monitoring stack
```bash
docker compose up --build
```
App http://localhost:8501 · metrics http://localhost:8000 · Prometheus http://localhost:9090 · Grafana http://localhost:3000 (admin/admin, dashboard "Car Price Predictor")

## Kubernetes + Terraform
```bash
cd terraform && terraform init && terraform apply     # namespaces + Prometheus/Grafana
kubectl apply -f k8s/                                 # app, service, HPA, ServiceMonitor
kubectl -n car-price port-forward svc/car-price-app 8501:80
kubectl -n monitoring port-forward svc/kube-prometheus-stack-grafana 3000:80
```
Set `kube_context` in `terraform/variables.tf` for your cluster (default `docker-desktop`).
The image in `k8s/deployment.yaml` is the one CI pushes to GHCR; make the package public or add an imagePullSecret.

## Deploy Streamlit (free)
Streamlit Community Cloud → New app → this repo, branch `main`, file `app/streamlit_app.py`.
The model trains automatically on first load.

## Metrics exposed (port 8000)
`car_price_predictions_total`, `car_price_prediction_errors_total`, `car_price_prediction_latency_seconds`, `car_price_predicted_inr`, `car_price_last_prediction_inr`
