# Multi-stage Dockerfile (Python 3.11)
FROM python:3.11-slim AS base

# Builder for wheels
FROM base AS builder
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
WORKDIR /wheels
# If you have requirements.txt, uncomment the next two lines:
# COPY requirements.txt /tmp/requirements.txt
# RUN pip wheel --wheel-dir=/wheels -r /tmp/requirements.txt || true

# Runtime
FROM base AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN useradd -m appuser
WORKDIR /app
# COPY --from=builder /wheels /wheels
# RUN pip install --no-cache-dir --find-links=/wheels -r /tmp/requirements.txt || true
COPY . /app
USER appuser
EXPOSE 8000
# Adjust the command to your app entrypoint (FastAPI example)
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
CMD ["python", "-V"]
