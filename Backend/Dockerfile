FROM python:3.11-slim

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

# Adjust if using FastAPI
CMD ["python", "app/main.py"]