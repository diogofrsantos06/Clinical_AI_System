FROM python:3.13-slim AS builder

# System dependencies for PostgreSQL
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Set root working directory
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

# Copy requirements from ROOT
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt 

FROM python:3.13-slim

RUN useradd -m -r appuser && mkdir /app && chown -R appuser /app

RUN apt-get update && apt-get install -y libpq-dev && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

# Copy Backend + Pipeline
COPY --chown=appuser:appuser Backend/ ./Backend
COPY --chown=appuser:appuser Pipeline/ ../Pipeline

# Make Pipeline visible to Python
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Move into backend folder
WORKDIR /app/Backend

USER appuser

EXPOSE 8000

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "Backend.wsgi:application"]
