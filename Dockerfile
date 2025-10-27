# Dockerfile for AGI Tracker Backend API
# Build from repository root

FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy backend service files (pyproject.toml has dependencies)
COPY services/etl/pyproject.toml services/etl/setup.py ./

# Install Python dependencies from pyproject.toml
RUN pip install --no-cache-dir -e .

# Copy entire services/etl directory
COPY services/etl /app

# Expose port (Railway will inject $PORT)
EXPOSE 8000

# Start uvicorn server (use python -m to ensure it's found)
CMD ["sh", "-c", "python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]

