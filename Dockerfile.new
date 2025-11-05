# Multi-stage Dockerfile for AGI Tracker ETL Service
# SECURITY: Non-root user, minimal runtime image, pinned dependencies
# GPT-5 Pro audit recommendations applied

# =============================================================================
# Stage 1: Builder - Install dependencies and build application
# =============================================================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first (layer caching)
COPY services/etl/pyproject.toml services/etl/setup.py ./
COPY services/etl/requirements.txt ./requirements.txt 2>/dev/null || true

# Install Python dependencies in a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e .

# =============================================================================
# Stage 2: Runtime - Minimal production image
# =============================================================================
FROM python:3.11-slim

WORKDIR /app

# Install only runtime dependencies (no build tools)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN adduser --disabled-password --gecos "" --uid 1000 appuser && \
    chown -R appuser:appuser /app

# Copy Python virtual environment from builder
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv

# Copy shared packages directory
COPY --chown=appuser:appuser packages /app/packages

# Copy application code
COPY --chown=appuser:appuser services/etl/app ./app

# Copy migrations and alembic config
COPY --chown=appuser:appuser infra/migrations ./migrations
COPY --chown=appuser:appuser infra/migrations/alembic.ini ./alembic.ini

# Copy supervisor configuration
COPY --chown=appuser:appuser services/etl/supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Set Python path to include virtual environment and packages
ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONPATH="/app:/app/packages/scoring/python:$PYTHONPATH"

# Switch to non-root user
USER appuser

# Expose port (Railway will override with PORT env var)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()"

# Start supervisor (manages migrations, API, Celery Beat)
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]

