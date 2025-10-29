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
    print(f"DATABASE_URL present: {bool(os.getenv('DATABASE_URL'))}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Migrations directory exists: {os.path.exists('/app/migrations')}")
    print(f"Alembic.ini exists: {os.path.exists('/app/alembic.ini')}")
    
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
            print("Migration output:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Migration failed with exit code {e.returncode}")
        if e.stdout:
            print(f"Migration stdout:\n{e.stdout}")
        if e.stderr:
            print(f"Migration stderr:\n{e.stderr}")
        print("⚠️  Continuing with server startup (migrations may have already been applied)")
        return False
    except FileNotFoundError as e:
        print(f"⚠️  Alembic command not found: {e}")
        print("⚠️  Continuing with server startup")
        return False
    except Exception as e:
        print(f"⚠️  Unexpected error during migration: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
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

