# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files
COPY pyproject.toml setup.py ./
COPY app ./app

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Copy start script
COPY start.sh ./
RUN chmod +x start.sh

# Expose port (Railway will override with PORT env var)
EXPOSE 8000

# Start command
CMD ["./start.sh"]
