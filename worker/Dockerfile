# Stage 1: builder
FROM python:3.10-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: final runtime image
FROM python:3.10-slim

RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --create-home appuser

WORKDIR /app

COPY --from=builder /root/.local /home/appuser/.local

COPY shared/ ./shared/
COPY worker/ ./worker/

RUN chown -R appuser:appgroup /app /home/appuser/.local

ENV PATH=/home/appuser/.local/bin:$PATH

USER appuser

CMD ["celery", "-A", "worker.celery_app", "worker", "--loglevel=info"]