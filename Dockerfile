FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY data/ data/
COPY src/ src/
COPY app/ app/
COPY .streamlit/ .streamlit/

# Bake the trained model into the image so containers start instantly
RUN python -m src.train

EXPOSE 8501 8000
HEALTHCHECK CMD python -c "import urllib.request as u; u.urlopen('http://localhost:8501/_stcore/health')"

CMD ["python", "app/serve.py"]
