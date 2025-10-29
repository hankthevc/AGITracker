#!/usr/bin/env python3
"""
Start server script for Railway deployment.
Runs database migrations before starting the FastAPI server.
"""
import os
import subprocess
import sys

def run_migrations():
    """Run Alembic migrations before starting the server."""
    print("🔄 Running database migrations...")
    try:
        # Change to migrations directory and run alembic upgrade
        result = subprocess.run(
            ["alembic", "-c", "/app/alembic.ini", "upgrade", "head"],
            cwd="/app/migrations",
            check=True,
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONPATH": "/app:/app/packages/scoring/python"}
        )
        print("✅ Migrations completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Migration failed: {e}")
        if e.stdout:
            print(f"stdout: {e.stdout}")
        if e.stderr:
            print(f"stderr: {e.stderr}")
        print("⚠️  Continuing with server startup (migrations may have already been applied)")
        return False
    except Exception as e:
        print(f"⚠️  Unexpected error during migration: {e}")
        print("⚠️  Continuing with server startup")
        return False

def main():
    """Main entry point."""
    # Run migrations first
    run_migrations()
    
    # Get port from environment variable
    port = os.environ.get("PORT", "8000")
    
    print(f"🚀 Starting FastAPI server on 0.0.0.0:{port}")
    
    # Start uvicorn
    os.execvp("uvicorn", [
        "uvicorn",
        "app.main:app",
        "--host", "0.0.0.0",
        "--port", port
    ])

if __name__ == "__main__":
    main()

