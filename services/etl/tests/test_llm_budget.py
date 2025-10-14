"""Unit tests for LLM budget tracking and management."""
import pytest
import redis
from datetime import datetime
from unittest.mock import patch, MagicMock
from app.tasks import llm_budget


@pytest.fixture
def mock_redis():
    """Mock Redis client for testing."""
    mock_client = MagicMock()
    with patch('app.tasks.llm_budget.redis_client', mock_client):
        yield mock_client


def test_get_daily_spend_new_day(mock_redis):
    """Test daily spend on a new day returns 0."""
    mock_redis.get.return_value = None
    
    spend = llm_budget.get_daily_spend()
    
    assert spend == 0.0
    # Should reset budget for new day
    mock_redis.set.assert_any_call(llm_budget.BUDGET_KEY, "0.0")


def test_get_daily_spend_existing(mock_redis):
    """Test daily spend retrieval with existing spend."""
    today = datetime.utcnow().date().isoformat()
    mock_redis.get.side_effect = [
        today.encode(),  # stored date matches
        b"5.75"  # current spend
    ]
    
    spend = llm_budget.get_daily_spend()
    
    assert spend == 5.75


def test_get_daily_spend_date_changed(mock_redis):
    """Test daily spend resets when date changes."""
    yesterday = "2024-01-01"
    mock_redis.get.side_effect = [
        yesterday.encode(),  # old date
        None
    ]
    
    spend = llm_budget.get_daily_spend()
    
    assert spend == 0.0
    # Should reset for new day
    calls = [call for call in mock_redis.set.call_args_list]
    assert any(llm_budget.BUDGET_KEY in str(call) for call in calls)


def test_add_spend(mock_redis):
    """Test adding to daily spend."""
    today = datetime.utcnow().date().isoformat()
    mock_redis.get.side_effect = [
        today.encode(),
        b"5.0"  # current spend
    ]
    
    new_total = llm_budget.add_spend(2.5)
    
    assert new_total == 7.5
    mock_redis.set.assert_called_with(llm_budget.BUDGET_KEY, "7.5")


def test_can_spend_within_budget(mock_redis):
    """Test can_spend returns True when within budget."""
    today = datetime.utcnow().date().isoformat()
    mock_redis.get.side_effect = [
        today.encode(),
        b"10.0"  # current spend
    ]
    
    with patch('app.tasks.llm_budget.settings') as mock_settings:
        mock_settings.llm_budget_daily_usd = 20.0
        
        result = llm_budget.can_spend(5.0)
        
        assert result is True


def test_can_spend_exceeds_budget(mock_redis):
    """Test can_spend returns False when would exceed budget."""
    today = datetime.utcnow().date().isoformat()
    mock_redis.get.side_effect = [
        today.encode(),
        b"18.0"  # current spend
    ]
    
    with patch('app.tasks.llm_budget.settings') as mock_settings:
        mock_settings.llm_budget_daily_usd = 20.0
        
        result = llm_budget.can_spend(5.0)
        
        assert result is False


def test_can_spend_exactly_at_budget(mock_redis):
    """Test can_spend returns True when exactly at budget limit."""
    today = datetime.utcnow().date().isoformat()
    mock_redis.get.side_effect = [
        today.encode(),
        b"15.0"  # current spend
    ]
    
    with patch('app.tasks.llm_budget.settings') as mock_settings:
        mock_settings.llm_budget_daily_usd = 20.0
        
        result = llm_budget.can_spend(5.0)
        
        assert result is True


def test_get_remaining_budget(mock_redis):
    """Test getting remaining budget."""
    today = datetime.utcnow().date().isoformat()
    mock_redis.get.side_effect = [
        today.encode(),
        b"12.5"  # current spend
    ]
    
    with patch('app.tasks.llm_budget.settings') as mock_settings:
        mock_settings.llm_budget_daily_usd = 20.0
        
        remaining = llm_budget.get_remaining_budget()
        
        assert remaining == 7.5


def test_get_remaining_budget_negative_clamped_to_zero(mock_redis):
    """Test remaining budget is clamped to 0 when over budget."""
    today = datetime.utcnow().date().isoformat()
    mock_redis.get.side_effect = [
        today.encode(),
        b"25.0"  # over budget
    ]
    
    with patch('app.tasks.llm_budget.settings') as mock_settings:
        mock_settings.llm_budget_daily_usd = 20.0
        
        remaining = llm_budget.get_remaining_budget()
        
        assert remaining == 0.0


def test_budget_guard_integration():
    """
    Integration-style test: verify budget guard behavior with very low budget.
    This simulates the scenario where budget is nearly exhausted.
    """
    with patch('app.tasks.llm_budget.redis_client') as mock_redis, \
         patch('app.tasks.llm_budget.settings') as mock_settings:
        
        today = datetime.utcnow().date().isoformat()
        mock_settings.llm_budget_daily_usd = 0.01  # Very low budget
        
        # Simulate already spent most of budget
        mock_redis.get.side_effect = [
            today.encode(),
            b"0.009"  # 0.009 spent, 0.001 remaining
        ]
        
        # Try to spend more than remaining
        can_proceed = llm_budget.can_spend(0.005)
        
        assert can_proceed is False, "Should not allow spending beyond budget"
        
        # Reset for next call
        mock_redis.get.side_effect = [
            today.encode(),
            b"0.009"
        ]
        
        # Verify remaining budget is minimal
        remaining = llm_budget.get_remaining_budget()
        assert remaining == pytest.approx(0.001, abs=1e-9), "Should have minimal budget remaining"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

