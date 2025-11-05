"""
Audit logging for admin actions.

SECURITY: All administrative actions should be logged for compliance and forensics.
"""

from datetime import datetime, UTC
from typing import Any
from fastapi import Request
from sqlalchemy.orm import Session


def log_admin_action(
    db: Session,
    request: Request,
    action: str,
    resource_type: str,
    resource_id: int | None = None,
    api_key: str | None = None,
    success: bool = True,
    error_message: str | None = None,
    metadata: dict[str, Any] | None = None
):
    """
    Log an administrative action to audit_logs table.
    
    Args:
        db: Database session
        request: FastAPI request (for IP, user agent)
        action: Action name ("approve", "reject", "retract", "trigger_ingestion")
        resource_type: Type of resource ("event", "mapping", "system")
        resource_id: ID of affected resource (optional)
        api_key: API key used (will be truncated to first 8 chars)
        success: Whether action succeeded
        error_message: Error message if failed
        metadata: Additional context (JSON)
    
    Note: Failure to log should not block the action - we log errors but continue.
    """
    try:
        # Truncate API key for security (first 8 chars only)
        api_key_hash = api_key[:8] + "..." if api_key and len(api_key) > 8 else None
        
        # Get client info from request
        client_host = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        # Create audit log entry
        from sqlalchemy import text
        db.execute(text("""
            INSERT INTO audit_logs 
            (timestamp, action, resource_type, resource_id, api_key_hash, 
             ip_address, user_agent, request_path, success, error_message, metadata)
            VALUES 
            (:timestamp, :action, :resource_type, :resource_id, :api_key_hash,
             :ip_address, :user_agent, :request_path, :success, :error_message, :metadata::jsonb)
        """), {
            "timestamp": datetime.now(UTC),
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "api_key_hash": api_key_hash,
            "ip_address": client_host,
            "user_agent": user_agent,
            "request_path": str(request.url.path) if request.url else None,
            "success": success,
            "error_message": error_message,
            "metadata": metadata or {}
        })
        db.commit()
    except Exception as e:
        # Logging failure should not block the action
        print(f"⚠️  Audit logging failed: {e}")
        # Don't raise - log error and continue

