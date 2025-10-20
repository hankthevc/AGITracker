"""
Event → Signpost mapper with alias-based matching + tier propagation.

Policy:
- A/B tier events can move gauges (subject to signpost's first_class)
- C/D tier events NEVER move gauges (displayed as "if true" only)
- Cap to max 2 signposts/event to avoid over-linking
- Confidence threshold for auto-approval: 0.6
"""
import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

ALIASES_PATH = Path(__file__).parent.parent.parent.parent / "infra" / "seeds" / "aliases_signposts.yaml"


def load_aliases() -> Dict:
    """Load alias registry from YAML."""
    if not ALIASES_PATH.exists():
        return {}
    with open(ALIASES_PATH) as f:
        return yaml.safe_load(f) or {}


def match_aliases(text: str, aliases: Dict) -> List[Tuple[str, float, str]]:
    """
    Match text against alias patterns and return (code, confidence, rationale) tuples.
    
    Returns up to 2 signposts per event to avoid over-linking.
    """
    text_lower = text.lower()
    matches = []
    seen_codes = set()
    
    for category, rules in aliases.items():
        if not isinstance(rules, list):
            continue
        for rule in rules:
            pattern = rule.get("pattern", "")
            codes = rule.get("codes", [])
            boost = rule.get("boost", 0.0)
            
            # Check if pattern matches
            try:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    for code in codes:
                        if code not in seen_codes:
                            base_conf = 0.5 + boost
                            rationale = f"Alias match: {pattern}"
                            matches.append((code, base_conf, rationale))
                            seen_codes.add(code)
            except re.error:
                # Invalid regex; skip
                continue
    
    # Cap to 2 signposts per event
    matches = matches[:2]
    return matches


def map_event_to_signposts(event, aliases: Dict = None) -> List[Tuple[str, float, str]]:
    """
    Map event to signposts using alias registry.
    
    Args:
        event: Event object or dict with title/summary
        aliases: Optional pre-loaded alias dict
    
    Returns:
        List of (signpost_code, confidence, tier) tuples
    """
    if aliases is None:
        aliases = load_aliases()
    
    # Combine title and summary for matching
    text = f"{event.get('title', '')} {event.get('summary', '')}" if isinstance(event, dict) else f"{event.title} {event.summary or ''}"
    
    # Match aliases
    candidates = match_aliases(text, aliases)
    
    # Add tier from event
    tier = event.get("evidence_tier") if isinstance(event, dict) else getattr(event, "evidence_tier", "D")
    
    results = []
    for code, conf, rationale in candidates:
        # Apply tier adjustments (A gets +0.1, B gets +0.05, C/D get 0)
        if tier == "A":
            conf += 0.1
        elif tier == "B":
            conf += 0.05
        # C and D get no boost (and will never move gauges anyway)
        
        # Cap at 0.95
        conf = min(conf, 0.95)
        
        results.append((code, conf, tier))
    
    return results


def needs_review(confidence: float, tier: str) -> bool:
    """Determine if event needs manual review based on confidence and tier."""
    # C/D always need review (they're "if true" only)
    if tier in ("C", "D"):
        return True
    # A/B need review if confidence < 0.6
    return confidence < 0.6
