FROM python:3.11-slim

# System dependencies for PostgreSQL
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Set root working directory
WORKDIR /app

# Copy requirements from ROOT
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy Backend + Pipeline
COPY Backend/ ./Backend
COPY Pipeline/ ./Pipeline

# Make Pipeline visible to Python
ENV PYTHONPATH=/app

# Move into backend folder
WORKDIR /app/Backend

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]