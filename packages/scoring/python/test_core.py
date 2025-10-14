"""Unit tests for Python scoring logic."""
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

import pytest
from core import (
    compute_signpost_progress,
    aggregate_category,
    compute_index_from_categories,
    compute_safety_margin,
)


def test_signpost_progress_ascending():
    """Test >= direction (higher is better)."""
    # Midpoint progress
    assert compute_signpost_progress(70, 50, 90, ">=") == 0.5
    
    # At target
    assert compute_signpost_progress(90, 50, 90, ">=") == 1.0
    
    # At baseline
    assert compute_signpost_progress(50, 50, 90, ">=") == 0.0
    
    # Clamping above target
    assert compute_signpost_progress(100, 50, 90, ">=") == 1.0
    
    # Clamping below baseline
    assert compute_signpost_progress(40, 50, 90, ">=") == 0.0


def test_signpost_progress_descending():
    """Test <= direction (lower is better)."""
    # Midpoint progress
    assert compute_signpost_progress(5, 10, 0, "<=") == 0.5
    
    # At target
    assert compute_signpost_progress(0, 10, 0, "<=") == 1.0
    
    # At baseline
    assert compute_signpost_progress(10, 10, 0, "<=") == 0.0
    
    # Clamping below target
    assert compute_signpost_progress(-5, 10, 0, "<=") == 1.0
    
    # Clamping above baseline
    assert compute_signpost_progress(15, 10, 0, "<=") == 0.0


def test_aggregate_category():
    """Test category aggregation with weighted mean."""
    # Equal weights
    result = aggregate_category([0.5, 0.8], [1.0, 1.0])
    assert result == 0.65
    
    # First-class weighting (2x)
    result = aggregate_category([0.5, 1.0], [2.0, 1.0])
    assert result == pytest.approx(2.0/3, rel=0.01)
    
    # All zeros
    result = aggregate_category([0.0, 0.0], [1.0, 1.0])
    assert result == 0.0
    
    # All ones
    result = aggregate_category([1.0, 1.0], [1.0, 1.0])
    assert result == 1.0
    
    # Single signpost
    result = aggregate_category([0.75], [1.0])
    assert result == 0.75


def test_harmonic_mean():
    """Test harmonic mean calculation in index computation."""
    weights = {"capabilities": 0.5, "agents": 0.0, "inputs": 0.5}
    categories = {"capabilities": 0.8, "agents": 0.0, "inputs": 0.2, "security": 0.0}
    
    result = compute_index_from_categories(categories, weights)
    
    # Combined capabilities = (0.8 * 0.5 + 0.0 * 0.0) / 0.5 = 0.8
    # Harmonic mean of 0.8 and 0.2:
    # H = 2 / (1/0.8 + 1/0.2) = 2 / (1.25 + 5) = 2 / 6.25 ≈ 0.32
    # But since agents is 0, combined_cap = 0.8
    # So H = 2 / (1/0.8 + 1/0.2) ≈ 0.32
    # Actually with weights, combined_cap = (0.8*0.5 + 0*0) / 0.5 = 0.8
    # Let me recalculate: the function does (cap*cap_weight + agents*agent_weight)/(cap_weight+agent_weight)
    # = (0.8*0.5 + 0*0) / 0.5 = 0.4/0.5 = 0.8
    # H(0.8, 0.2) = 2/(1.25+5) = 2/6.25 = 0.32
    # But wait, let me check the actual output. It says 0.2909...
    # Let me trace through: combined_cap with agents=0 and cap=0.8, weights 0.5,0:
    # combined_cap = (0.8*0.5 + 0*0) / (0.5+0) = 0.4/0.5 = 0.8
    # H(0.8, 0.2) = 2 / (1/0.8 + 1/0.2) = 2/(1.25 + 5) = 2/6.25 = 0.32
    # But the output is 0.29... Hmm, let me check if agents has default weight
    # Looking at code: cap_weight = preset_weights.get("capabilities", 0.25), agent_weight = preset_weights.get("agents", 0.25)
    # So if I pass {"capabilities": 0.5, "inputs": 0.5}, agents defaults to 0.25!
    # combined_cap = (0.8*0.5 + 0*0.25) / (0.5+0.25) = 0.4/0.75 = 0.533...
    # H(0.533, 0.2) = 2/(1/0.533 + 1/0.2) = 2/(1.876 + 5) = 2/6.876 ≈ 0.291
    # That matches! So I need to explicitly set agents weight to 0
    # With agents=0, combined_cap = (0.8*0.5)/(0.5) = 0.8
    # H(0.8, 0.2) = 2/(1/0.8 + 1/0.2) = 2/6.25 = 0.32
    assert 0.31 < result["overall"] < 0.33
    
    # Safety margin should be 0.0 - combined_cap
    # combined_cap = 0.8, safety_margin = 0 - 0.8 = -0.8
    assert result["safety_margin"] == pytest.approx(-0.8, abs=0.01)


def test_harmonic_mean_edge_cases():
    """Test edge cases for harmonic mean."""
    weights = {"capabilities": 0.5, "agents": 0.0, "inputs": 0.5}
    
    # When inputs is 0, harmonic mean should be 0
    categories = {"capabilities": 0.5, "agents": 0.0, "inputs": 0.0, "security": 0.0}
    result = compute_index_from_categories(categories, weights)
    assert result["overall"] == 0.0
    
    # When both are 0
    categories = {"capabilities": 0.0, "agents": 0.0, "inputs": 0.0, "security": 0.0}
    result = compute_index_from_categories(categories, weights)
    assert result["overall"] == 0.0
    
    # When both capabilities and inputs are 1
    categories = {"capabilities": 1.0, "agents": 0.0, "inputs": 1.0, "security": 0.0}
    result = compute_index_from_categories(categories, weights)
    # combined_cap = (1.0*0.5 + 0*0) / 0.5 = 1.0
    # H(1.0, 1.0) = 2/(1 + 1) = 1.0
    assert result["overall"] == 1.0


def test_safety_margin():
    """Test safety margin calculation."""
    # Security ahead (security=0.5, capabilities=0.3)
    margin = compute_safety_margin(0.5, 0.3)
    assert margin == pytest.approx(0.2)
    
    # Capabilities ahead (negative margin - danger zone)
    margin = compute_safety_margin(0.4, 0.7)
    assert margin == pytest.approx(-0.3)
    
    # Equal (no margin)
    margin = compute_safety_margin(0.5, 0.5)
    assert margin == pytest.approx(0.0)


def test_weighted_presets():
    """Test different preset weightings."""
    # Aschenbrenner weights capabilities more heavily
    aschenbrenner_weights = {
        "capabilities": 0.6,
        "agents": 0.0,
        "inputs": 0.4,
    }
    
    categories = {"capabilities": 0.8, "agents": 0.0, "inputs": 0.4, "security": 0.0}
    result = compute_index_from_categories(categories, aschenbrenner_weights)
    
    # combined_cap = (0.8*0.6 + 0*0) / 0.6 = 0.8
    # H(0.8, 0.4) = 2 / (1/0.8 + 1/0.4) = 2/(1.25 + 2.5) = 2/3.75 ≈ 0.533
    assert result["overall"] == pytest.approx(0.533, abs=0.01)
    
    # Equal weights
    equal_weights = {"capabilities": 0.5, "agents": 0.0, "inputs": 0.5}
    result_equal = compute_index_from_categories(categories, equal_weights)
    
    # combined_cap = (0.8*0.5) / 0.5 = 0.8
    # H(0.8, 0.4) = 0.533 (same as above since combined_cap is still 0.8)
    assert result_equal["overall"] == pytest.approx(0.533, abs=0.01)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

