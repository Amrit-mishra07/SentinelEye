# ==============================================================================
# SentinelEye - Sovereign Air-Gapped Satellite Intelligence Container
# Designed for Smart India Hackathon (SIH) 2026 - Problem Statement PS26227
# Runs 100% offline with Docker networking completely severed (--net none)
# ==============================================================================

FROM python:3.11-slim

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Air-gap enforcement flags
ENV OFFLINE_MODE=true
ENV HF_HUB_OFFLINE=1
ENV TRANSFORMERS_OFFLINE=1
ENV REPLAY_MODE=true

# 1. Install system geospatial libraries & graphics headers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgdal-dev \
    gdal-bin \
    libgl1 \
    libglib2.0-0 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL environment variables
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

WORKDIR /app

# 2. Install pinned dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# 3. Copy application components
COPY schemas/ ./schemas/
COPY pipeline/ ./pipeline/
COPY api/ ./api/
COPY ingestion/ ./ingestion/
COPY retrieval/ ./retrieval/
COPY change_detection/ ./change_detection/
COPY llm_briefing/ ./llm_briefing/
COPY audit/ ./audit/
COPY frontend/ ./frontend/
COPY scripts/ ./scripts/
COPY tests/ ./tests/
COPY docs/ ./docs/
COPY data/precomputed/ ./data/precomputed/
COPY models/MODEL_CATALOG.md ./models/MODEL_CATALOG.md
COPY .env.example ./.env
COPY README.md INTEGRATION.md DEMO_FALLBACK.md ./

# Make scripts executable
RUN chmod +x scripts/*.sh scripts/*.py

# Expose Streamlit dashboard and local FastAPI ports
EXPOSE 8501 8000

# Healthcheck ensuring offline readiness
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD python3 scripts/verify_offline_env.py || exit 1

# Default command: launch the tactical analyst dashboard
CMD ["streamlit", "run", "frontend/app.py", "--server.port=8501", "--server.headless=true", "--server.address=0.0.0.0"]
