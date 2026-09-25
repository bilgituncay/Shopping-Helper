# Stage 1: Builder

FROM python:3.10-slim AS builder

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime image

FROM python:3.10-slim

WORKDIR /app

COPY --from=builder /root/.local /root/.local

COPY shared/ ./shared/
COPY api/ ./api/

ENV PATH=/root/.local/bin:$PATH

EXPOSE 8000

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]