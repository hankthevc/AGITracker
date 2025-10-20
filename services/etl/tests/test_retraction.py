"""Unit tests for retraction system."""
import pytest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from app.models import Event, EventSignpostLink


class TestRetractionIdempotency:
    """Test that retracting an event twice is safe (idempotent)."""
    
    def test_retract_already_retracted_event(self, client, db_session, sample_event, api_key_header):
        """Retracting an already-retracted event should return success, not error."""
        # First retraction
        response1 = client.post(
            f"/v1/admin/retract",
            json={
                "event_id": sample_event.id,
                "reason": "Initial retraction",
                "evidence_url": "https://example.com/correction"
            },
            headers=api_key_header
        )
        
        assert response1.status_code == 200
        assert response1.json()["status"] == "retracted"
        
        # Second retraction (idempotent)
        response2 = client.post(
            f"/v1/admin/retract",
            json={
                "event_id": sample_event.id,
                "reason": "Duplicate retraction",
                "evidence_url": "https://example.com/correction2"
            },
            headers=api_key_header
        )
        
        assert response2.status_code == 200
        assert response2.json()["status"] == "already_retracted"
        assert response2.json()["reason"] == "Initial retraction"  # Original reason preserved
    
    def test_retraction_excluded_from_queries(self, client, db_session, sample_event):
        """Retracted events should not appear in public endpoints."""
        # Get initial count
        response_before = client.get("/v1/events")
        events_before = response_before.json()["results"]
        count_before = len(events_before)
        
        # Retract the event
        sample_event.retracted = True
        sample_event.retracted_at = datetime.now(timezone.utc)
        db_session.commit()
        
        # Check it's excluded
        response_after = client.get("/v1/events")
        events_after = response_after.json()["results"]
        count_after = len(events_after)
        
        assert count_after == count_before - 1
        assert sample_event.id not in [e["id"] for e in events_after]
    
    @patch("app.utils.cache.invalidate_signpost_caches")
    async def test_retraction_invalidates_cache(self, mock_invalidate, client, db_session, sample_event, api_key_header):
        """Retracting an event should invalidate related caches."""
        # Create a signpost link
        link = EventSignpostLink(
            event_id=sample_event.id,
            signpost_id=1,
            confidence=0.9
        )
        db_session.add(link)
        db_session.commit()
        
        # Retract the event
        response = client.post(
            f"/v1/admin/retract",
            json={
                "event_id": sample_event.id,
                "reason": "Test retraction"
            },
            headers=api_key_header
        )
        
        assert response.status_code == 200
        # Verify cache invalidation was called
        mock_invalidate.assert_called_once()
        called_signpost_ids = mock_invalidate.call_args[0][0]
        assert 1 in called_signpost_ids

