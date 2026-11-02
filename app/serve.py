"""Container entrypoint: open the Prometheus /metrics port at startup, then run Streamlit.

Streamlit only executes the app script when a browser connects, so starting the
metrics server there would leave Prometheus scraping a closed port until the first visit.
"""
import os
import sys

from prometheus_client import start_http_server
from streamlit.web import cli as stcli

if __name__ == "__main__":
    start_http_server(int(os.getenv("METRICS_PORT", "8000")))
    sys.argv = ["streamlit", "run", "app/streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
    sys.exit(stcli.main())
