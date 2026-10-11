# Stage 1: Builder

FROM python:3.10-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime image

FROM python:3.10-slim

RUN groupadd --gid 1000 appgroup && \
    useradd --uid 1000 --gid appgroup --create-home appuser

WORKDIR /app

COPY --from=builder /root/.local /home/appuser/.local

COPY shared/ ./shared/
COPY api/ ./api/
COPY scripts/__init__.py scripts/init_db.py scripts/seed_test_data.py ./scripts/

RUN chown -R appuser:appgroup /app /home/appuser/.local

ENV PATH=/home/appuser/.local/bin:$PATH

USER appuser

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]