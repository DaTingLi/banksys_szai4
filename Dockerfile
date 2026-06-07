ARG PIP_INDEX_URL=https://pypi.org/simple
FROM python:3.11-slim

# Re-declare ARG after FROM (ARG scope ends at FROM)
ARG PIP_INDEX_URL

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Copy requirements and install production dependencies only
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 120 --index-url "${PIP_INDEX_URL}" -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY data/ ./data/

# Train the model at build time so the prediction service has an artifact.
# model.pkl is gitignored (never committed); it is baked into the image here.
RUN python -m app.ml.train --overwrite

# Expose Streamlit default port (will be mapped to 8004 on host)
EXPOSE 8501

# Health check via Python stdlib (avoids installing curl through the slow
# Debian mirror on the deploy server; Streamlit exposes /_stcore/health).
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8501/_stcore/health').status==200 else 1)" || exit 1

# Run Streamlit
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
