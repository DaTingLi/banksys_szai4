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

# Expose Streamlit default port (will be mapped to 8004 on host)
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -fSs http://localhost:8501/health || exit 1

# Run Streamlit
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
