# ABOS — Agentic Business Operating System
FROM python:3.11-slim

# System deps for coincurve (fast Nostr signing) build
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libsecp256k1-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Seed the six demo tenants at build time so demo_state.json is baked in
RUN python3 scripts/seed_demo.py

EXPOSE 8000

CMD ["uvicorn", "abos.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
