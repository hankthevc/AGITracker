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

ALIASES_PATH = Path(__file__).parent.parent.parent.parent.parent / "infra" / "seeds" / "aliases_signposts.yaml"


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
    
    # Aliases structure: {category: [{pattern, codes, boost}, ...]}
    for category, rules in aliases.items():
        if not isinstance(rules, list):
            continue
        for rule in rules:
            if not isinstance(rule, dict):
                continue
            pattern = rule.get("pattern", "")
            codes = rule.get("codes", [])
            boost = rule.get("boost", 0.0)
            
            # Check if pattern matches
            try:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    for code in codes:
                        if code not in seen_codes:
                            base_conf = 0.5 + boost
                            rationale = f"Alias match: '{pattern}'"
                            matches.append((code, base_conf, rationale))
                            seen_codes.add(code)
                            if len(matches) >= 2:  # Early exit at cap
                                return matches
            except re.error:
                # Invalid regex; skip
                continue
    
    # Cap to 2 signposts per event
    return matches[:2]


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


def map_all_unmapped_events() -> Dict:
    """
    Map all events that don't have signpost links yet.
    
    Uses rule-based aliases first, then LLM fallback if enabled and budget allows.
    
    Returns:
        Statistics dict with processed/linked/needs_review/unmapped counts
    """
    from app.database import SessionLocal
    from app.models import Event, EventSignpostLink, Signpost
    from datetime import datetime, timezone
    from app.config import settings
    
    db = SessionLocal()
    stats = {"processed": 0, "linked": 0, "needs_review": 0, "unmapped": 0, "llm_used": 0}
    
    try:
        # Find events without links
        events = db.query(Event).outerjoin(EventSignpostLink).filter(
            EventSignpostLink.event_id.is_(None)
        ).all()
        
        print(f"📍 Mapping {len(events)} unmapped events to signposts...")
        aliases = load_aliases()
        
        # Get all signpost codes for LLM
        all_signpost_codes = [sp.code for sp in db.query(Signpost.code).all()]
        
        for event in events:
            # Try rule-based first
            results = map_event_to_signposts(event, aliases)
            stats["processed"] += 1
            
            # LLM fallback if no matches and LLM enabled
            if not results and settings.enable_llm_mapping and settings.openai_api_key:
                try:
                    from app.utils.llm_news_parser import parse_event_with_llm
                    llm_results = parse_event_with_llm(
                        event.title,
                        event.summary or "",
                        all_signpost_codes,
                        event.evidence_tier
                    )
                    if llm_results:
                        results = llm_results
                        stats["llm_used"] += 1
                        print(f"  🤖 LLM fallback used for: {event.title[:50]}...")
                except Exception as e:
                    print(f"  ⚠️  LLM fallback failed: {e}")
            
            if not results:
                stats["unmapped"] += 1
                event.needs_review = True
                db.commit()
                continue
            
            # Create links
            links_created = 0
            max_conf = 0.0
            for code, conf, tier in results:
                signpost = db.query(Signpost).filter(Signpost.code == code).first()
                if not signpost:
                    continue
                
                # Policy: C/D tier adds rationale note
                rationale = f"Auto-mapped via alias registry (conf={conf:.2f})"
                if tier in ("C", "D"):
                    rationale += " [C/D tier: displayed but NEVER moves gauges]"
                
                link = EventSignpostLink(
                    event_id=event.id,
                    signpost_id=signpost.id,
                    confidence=conf,
                    rationale=rationale,
                    observed_at=event.published_at or event.ingested_at,
                    value=None,
                )
                db.add(link)
                links_created += 1
                max_conf = max(max_conf, conf)
            
            if links_created > 0:
                stats["linked"] += 1
                # Set needs_review based on tier and confidence
                event.needs_review = needs_review(max_conf, event.evidence_tier)
                if event.needs_review:
                    stats["needs_review"] += 1
                event.parsed = {
                    **(event.parsed or {}),
                    "mapped_at": datetime.now(timezone.utc).isoformat(),
                    "max_confidence": max_conf,
                }
                db.commit()
                print(f"  ✓ Mapped: {event.title[:50]}... → {links_created} signposts (conf: {max_conf:.2f})")
        
        print(f"\n✅ Mapping complete!")
        print(f"   Processed: {stats['processed']}, Linked: {stats['linked']}, Needs review: {stats['needs_review']}, Unmapped: {stats['unmapped']}")
        return stats
    
    finally:
        db.close()
