#!/usr/bin/env python3
"""Startup script for Railway deployment."""
import os
import sys

# Get port from environment variable
port = os.environ.get("PORT", "8000")

# Start uvicorn
os.execvp("uvicorn", [
    "uvicorn",
    "app.main:app",
    "--host", "0.0.0.0",
    "--port", port
])

