#!/usr/bin/env python3
"""
Audit script for checking source URLs in events.

Usage:
    python scripts/audit_source_urls.py

Output:
    Creates JSON report in infra/reports/url_audit_YYYY-MM-DD.json
"""
import json
import sys
from datetime import datetime, UTC
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import requests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from services.etl.app.config import settings
from services.etl.app.models import Event


def validate_url(url: str, timeout: int = 10) -> dict:
    """
    Validate a URL is accessible.
    
    Args:
        url: URL to check
        timeout: Request timeout in seconds
        
    Returns:
        Dict with validation results
    """
    if not url:
        return {
            "valid": False,
            "status_code": None,
            "final_url": None,
            "redirect_count": 0,
            "error": "Empty URL",
            "checked_at": datetime.now(UTC).isoformat()
        }
    
    try:
        # Use HEAD request to save bandwidth
        response = requests.head(
            url, 
            timeout=timeout, 
            allow_redirects=True,
            headers={'User-Agent': 'AGI-Tracker-URL-Validator/1.0'}
        )
        
        return {
            "valid": response.status_code < 400,
            "status_code": response.status_code,
            "final_url": response.url,
            "redirect_count": len(response.history),
            "error": None if response.status_code < 400 else f"HTTP {response.status_code}",
            "checked_at": datetime.now(UTC).isoformat()
        }
    except requests.exceptions.Timeout:
        return {
            "valid": False,
            "status_code": None,
            "final_url": None,
            "redirect_count": 0,
            "error": "Timeout",
            "checked_at": datetime.now(UTC).isoformat()
        }
    except requests.exceptions.ConnectionError as e:
        return {
            "valid": False,
            "status_code": None,
            "final_url": None,
            "redirect_count": 0,
            "error": f"Connection error: {str(e)[:100]}",
            "checked_at": datetime.now(UTC).isoformat()
        }
    except requests.exceptions.SSLError as e:
        return {
            "valid": False,
            "status_code": None,
            "final_url": None,
            "redirect_count": 0,
            "error": f"SSL error: {str(e)[:100]}",
            "checked_at": datetime.now(UTC).isoformat()
        }
    except requests.exceptions.TooManyRedirects:
        return {
            "valid": False,
            "status_code": None,
            "final_url": None,
            "redirect_count": 999,
            "error": "Too many redirects (loop detected)",
            "checked_at": datetime.now(UTC).isoformat()
        }
    except Exception as e:
        return {
            "valid": False,
            "status_code": None,
            "final_url": None,
            "redirect_count": 0,
            "error": f"Unknown error: {str(e)[:100]}",
            "checked_at": datetime.now(UTC).isoformat()
        }


def main():
    """Run URL audit on all events."""
    print("🔍 Starting URL audit...")
    
    # Create database connection
    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Get all events
        events = db.query(Event).order_by(Event.id).all()
        total_events = len(events)
        
        print(f"📊 Found {total_events} events to check")
        
        # Validate each URL
        results = []
        valid_count = 0
        invalid_count = 0
        
        for i, event in enumerate(events, 1):
            print(f"[{i}/{total_events}] Checking event {event.id}: {event.title[:50]}...")
            
            if not event.source_url:
                print(f"  ⚠️  No URL")
                result = {
                    "event_id": event.id,
                    "title": event.title,
                    "url": None,
                    **validate_url(None)
                }
                invalid_count += 1
            else:
                validation = validate_url(event.source_url)
                result = {
                    "event_id": event.id,
                    "title": event.title,
                    "url": event.source_url,
                    **validation
                }
                
                if validation["valid"]:
                    print(f"  ✅ Valid (HTTP {validation['status_code']})")
                    valid_count += 1
                else:
                    print(f"  ❌ Invalid: {validation['error']}")
                    invalid_count += 1
            
            results.append(result)
            
            # Rate limiting: 2 requests per second
            if i < total_events:
                import time
                time.sleep(0.5)
        
        # Create report
        report = {
            "audit_date": datetime.now(UTC).isoformat(),
            "total_events": total_events,
            "urls_checked": total_events,
            "valid": valid_count,
            "invalid": invalid_count,
            "results": results,
            "issues": [r for r in results if not r["valid"]]
        }
        
        # Save report
        reports_dir = Path(__file__).parent.parent / "infra" / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        report_file = reports_dir / f"url_audit_{datetime.now(UTC).strftime('%Y-%m-%d')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print("\n" + "="*60)
        print(f"📋 Audit Complete!")
        print(f"   Total events: {total_events}")
        print(f"   Valid URLs: {valid_count} ({valid_count/total_events*100:.1f}%)")
        print(f"   Invalid URLs: {invalid_count} ({invalid_count/total_events*100:.1f}%)")
        print(f"   Report saved: {report_file}")
        print("="*60)
        
        if invalid_count > 0:
            print("\n⚠️  Issues found:")
            for issue in report["issues"][:10]:  # Show first 10
                print(f"   - Event {issue['event_id']}: {issue['error']}")
                print(f"     URL: {issue['url']}")
            if invalid_count > 10:
                print(f"   ... and {invalid_count - 10} more (see report)")
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
