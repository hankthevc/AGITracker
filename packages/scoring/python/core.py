"""Core scoring algorithms for AGI signpost progress calculation."""
from typing import Dict, List, Optional


def clamp(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Clamp a value between min and max."""
    return max(min_val, min(max_val, value))


def compute_signpost_progress(
    observed: float,
    baseline: float,
    target: float,
    direction: str
) -> float:
    """
    Compute progress for a single signpost.
    
    Args:
        observed: Current observed value
        baseline: Starting baseline value
        target: Target value for completion
        direction: '>=' for increasing metrics, '<=' for decreasing
    
    Returns:
        Progress value between 0 and 1
    """
    if direction == ">=":
        if target == baseline:
            return 1.0 if observed >= target else 0.0
        return clamp((observed - baseline) / (target - baseline))
    elif direction == "<=":
        if baseline == target:
            return 1.0 if observed <= target else 0.0
        return clamp((baseline - observed) / (baseline - target))
    else:
        raise ValueError(f"Invalid direction: {direction}. Must be '>=' or '<='")


def aggregate_category(
    signpost_progresses: List[float],
    signpost_weights: Optional[List[float]] = None
) -> float:
    """
    Aggregate multiple signpost progresses into a category score.
    
    Args:
        signpost_progresses: List of individual signpost progress values (0-1)
        signpost_weights: Optional weights for each signpost. Defaults to equal weighting.
    
    Returns:
        Weighted mean category progress (0-1)
    """
    if not signpost_progresses:
        return 0.0
    
    if signpost_weights is None:
        signpost_weights = [1.0] * len(signpost_progresses)
    
    if len(signpost_progresses) != len(signpost_weights):
        raise ValueError("signpost_progresses and signpost_weights must have same length")
    
    total_weight = sum(signpost_weights)
    if total_weight == 0:
        return 0.0
    
    weighted_sum = sum(p * w for p, w in zip(signpost_progresses, signpost_weights))
    return weighted_sum / total_weight


def compute_overall(capabilities: float, inputs: float) -> float:
    """
    Compute overall AGI proximity using harmonic mean.
    
    The harmonic mean ensures that both capabilities AND inputs must advance
    together - bottleneck on either dimension significantly reduces overall score.
    
    Args:
        capabilities: Capabilities category score (0-1)
        inputs: Inputs category score (0-1)
    
    Returns:
        Overall proximity score (0-1)
    """
    if capabilities == 0 or inputs == 0:
        return 0.0
    
    return 2.0 / (1.0 / capabilities + 1.0 / inputs)


def compute_safety_margin(security: float, capabilities: float) -> float:
    """
    Compute safety margin (security minus capabilities).
    
    Negative values indicate capabilities are outpacing security readiness.
    
    Args:
        security: Security category score (0-1)
        capabilities: Capabilities category score (0-1)
    
    Returns:
        Safety margin (-1 to 1)
    """
    return security - capabilities


def compute_index_from_categories(
    category_scores: Dict[str, float],
    preset_weights: Dict[str, float]
) -> Dict[str, float]:
    """
    Compute full index metrics from category scores using preset weights.
    
    Args:
        category_scores: Dict with 'capabilities', 'agents', 'inputs', 'security'
        preset_weights: Dict with category weights (must sum to ~1.0)
    
    Returns:
        Dict with overall, safety_margin, and all category scores
    """
    capabilities = category_scores.get("capabilities", 0.0)
    agents = category_scores.get("agents", 0.0)
    inputs = category_scores.get("inputs", 0.0)
    security = category_scores.get("security", 0.0)
    
    # Combine capabilities and agents into effective "capabilities API"
    # Use weighted average for now (can be refined)
    cap_weight = preset_weights.get("capabilities", 0.25)
    agent_weight = preset_weights.get("agents", 0.25)
    combined_cap = (
        (capabilities * cap_weight + agents * agent_weight) / 
        (cap_weight + agent_weight) if (cap_weight + agent_weight) > 0 else 0.0
    )
    
    overall = compute_overall(combined_cap, inputs)
    safety_margin = compute_safety_margin(security, combined_cap)
    
    return {
        "capabilities": capabilities,
        "agents": agents,
        "inputs": inputs,
        "security": security,
        "overall": overall,
        "safety_margin": safety_margin,
    }


def compute_confidence_bands(
    category_scores: Dict[str, float],
    evidence_counts: Dict[str, Dict[str, int]],
    confidence_width: float = 0.1
) -> Dict[str, Dict[str, float]]:
    """
    Compute confidence bands around index values based on evidence quality.
    
    Args:
        category_scores: Category score values
        evidence_counts: Counts of A/B/C/D tier evidence per category
        confidence_width: Base width of confidence interval (default 0.1 = ±5%)
    
    Returns:
        Dict of {category: {lower, upper}} confidence bounds
    """
    bands = {}
    
    for category, score in category_scores.items():
        if category in ["overall", "safety_margin"]:
            # Derived metrics use combined uncertainty
            bands[category] = {"lower": max(0, score - confidence_width), "upper": min(1, score + confidence_width)}
            continue
        
        counts = evidence_counts.get(category, {"A": 0, "B": 0, "C": 0, "D": 0})
        total = sum(counts.values())
        
        if total == 0:
            # No evidence = maximum uncertainty
            bands[category] = {"lower": 0.0, "upper": 1.0}
            continue
        
        # Weight evidence quality: A=1.0, B=0.8, C=0.3, D=0.1
        quality_score = (
            counts.get("A", 0) * 1.0 +
            counts.get("B", 0) * 0.8 +
            counts.get("C", 0) * 0.3 +
            counts.get("D", 0) * 0.1
        ) / total
        
        # Lower quality = wider bands
        adjusted_width = confidence_width / quality_score if quality_score > 0 else 1.0
        adjusted_width = min(adjusted_width, 0.5)  # Cap at ±25%
        
        bands[category] = {
            "lower": max(0.0, score - adjusted_width),
            "upper": min(1.0, score + adjusted_width),
        }
    
    return bands

