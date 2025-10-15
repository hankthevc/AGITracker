"""
Event → Signpost mapper with heuristic rules + optional LLM fallback.

Policy:
- A/B tier events can move gauges
- C/D tier events NEVER move gauges (displayed as "if true" only)
- Confidence threshold for auto-approval: 0.6
- Below threshold → needs_review=True
"""
import re
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timezone

from app.database import SessionLocal
from app.models import Event, EventSignpostLink, Signpost, EventEntity


# Keyword → signpost code mapping (case-insensitive)
KEYWORD_SIGNPOST_MAP = {
    # SWE-bench
    "swe-bench verified": ["swe_bench_85", "swe_bench_90"],
    "swe-bench": ["swe_bench_85", "swe_bench_90"],
    "software engineering": ["swe_bench_85"],
    
    # OSWorld
    "osworld": ["osworld_50", "osworld_65", "osworld_85"],
    "os-world": ["osworld_50", "osworld_65", "osworld_85"],
    "computer use": ["osworld_50"],
    
    # WebArena
    "webarena": ["webarena_60", "webarena_70", "webarena_85"],
    "web-arena": ["webarena_60", "webarena_70", "webarena_85"],
    "visualwebarena": ["webarena_70", "webarena_85"],
    "web navigation": ["webarena_60"],
    
    # GPQA
    "gpqa diamond": ["gpqa_75", "gpqa_sota", "gpqa_phd_parity"],
    "gpqa": ["gpqa_75", "gpqa_sota"],
    "graduate-level": ["gpqa_75"],
    "phd-level": ["gpqa_phd_parity"],
    
    # HLE (monitor-only)
    "humanity's last exam": ["hle_text_50", "hle_text_70"],
    "hle": ["hle_text_50", "hle_text_70"],
    
    # Compute
    "10^26": ["compute_1e26"],
    "1e26": ["compute_1e26"],
    "10^27": ["compute_1e27"],
    "1e27": ["compute_1e27"],
    "flop": ["compute_1e26", "compute_1e27"],
    
    # Data center power
    "1 gw": ["dc_power_1gw"],
    "10 gw": ["dc_power_10gw"],
    "gigawatt": ["dc_power_1gw", "dc_power_10gw"],
    "datacenter": ["dc_power_1gw"],
}


# Numeric value patterns
PERCENTAGE_PATTERN = re.compile(r'(\d+(?:\.\d+)?)\s*%')
FLOP_PATTERN = re.compile(r'10\^(\d+)|1e(\d+)', re.IGNORECASE)
POWER_PATTERN = re.compile(r'(\d+(?:\.\d+)?)\s*gw', re.IGNORECASE)


def extract_numeric_values(text: str) -> Dict[str, Optional[float]]:
    """
    Extract numeric values from event text.
    
    Returns:
        dict with 'percentage', 'flops_exponent', 'power_gw' keys
    """
    text_lower = text.lower()
    
    result = {
        "percentage": None,
        "flops_exponent": None,
        "power_gw": None
    }
    
    # Extract percentage
    pct_match = PERCENTAGE_PATTERN.search(text)
    if pct_match:
        result["percentage"] = float(pct_match.group(1))
    
    # Extract FLOP exponent
    flop_match = FLOP_PATTERN.search(text)
    if flop_match:
        exp = flop_match.group(1) or flop_match.group(2)
        result["flops_exponent"] = int(exp)
    
    # Extract power in GW
    power_match = POWER_PATTERN.search(text)
    if power_match:
        result["power_gw"] = float(power_match.group(1))
    
    return result


def match_keywords_to_signposts(text: str, db) -> List[Tuple[str, float, str]]:
    """
    Match keywords in text to signpost codes with confidence.
    
    Returns:
        List of (signpost_code, confidence, rationale) tuples
    """
    text_lower = text.lower()
    matches = []
    matched_codes = set()
    
    # Get all signpost codes from DB for validation
    valid_codes = {sp.code for sp in db.query(Signpost.code).all()}
    
    for keyword, signpost_codes in KEYWORD_SIGNPOST_MAP.items():
        if keyword in text_lower:
            for code in signpost_codes:
                if code in valid_codes and code not in matched_codes:
                    # Base confidence: 0.5 for keyword match
                    confidence = 0.5
                    rationale = f"Keyword match: '{keyword}'"
                    
                    matches.append((code, confidence, rationale))
                    matched_codes.add(code)
    
    return matches


def calculate_final_confidence(
    base_confidence: float,
    has_numeric: bool,
    multiple_matches: bool,
    evidence_tier: str
) -> float:
    """
    Calculate final confidence score based on multiple factors.
    
    Policy adjustments:
    - +0.2 if numeric value extracted
    - +0.2 if multiple independent cues
    - +0.1 for A-tier sources
    - +0.05 for B-tier sources
    - No boost for C/D tier
    - Cap at 0.95
    """
    confidence = base_confidence
    
    if has_numeric:
        confidence += 0.2
    
    if multiple_matches:
        confidence += 0.2
    
    # Tier adjustments
    if evidence_tier == "A":
        confidence += 0.1
    elif evidence_tier == "B":
        confidence += 0.05
    # C and D get no boost (and never move gauges anyway)
    
    return min(confidence, 0.95)


def refine_with_numeric_context(
    matches: List[Tuple[str, float, str]],
    numeric_values: Dict,
    db
) -> List[Tuple[str, float, str, Optional[float]]]:
    """
    Refine matches using extracted numeric values.
    
    Returns:
        List of (signpost_code, confidence, rationale, value) tuples
    """
    refined = []
    
    for code, confidence, rationale in matches:
        value = None
        updated_rationale = rationale
        
        # Get signpost details
        signpost = db.query(Signpost).filter(Signpost.code == code).first()
        if not signpost:
            continue
        
        # Match numeric values to signpost type
        if "swe_bench" in code or "osworld" in code or "webarena" in code or "gpqa" in code or "hle" in code:
            if numeric_values.get("percentage"):
                value = numeric_values["percentage"]
                updated_rationale += f" + percentage value: {value}%"
                confidence += 0.15  # Boost for specific value
        
        elif "compute" in code:
            if numeric_values.get("flops_exponent"):
                exp = numeric_values["flops_exponent"]
                value = 10 ** exp
                updated_rationale += f" + FLOP magnitude: 10^{exp}"
                confidence += 0.15
        
        elif "dc_power" in code:
            if numeric_values.get("power_gw"):
                value = numeric_values["power_gw"]
                updated_rationale += f" + power value: {value} GW"
                confidence += 0.15
        
        refined.append((code, min(confidence, 0.95), updated_rationale, value))
    
    return refined


def map_event_to_signposts(event_id: int, db) -> Dict:
    """
    Map a single event to signposts using heuristic rules.
    
    Returns:
        dict with 'linked', 'needs_review', 'confidence_scores'
    """
    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        return {"error": "Event not found"}
    
    # Combine title and summary for matching
    text = f"{event.title} {event.summary or ''}"
    
    # Extract numeric values
    numeric_values = extract_numeric_values(text)
    has_numeric = any(v is not None for v in numeric_values.values())
    
    # Match keywords to signposts
    keyword_matches = match_keywords_to_signposts(text, db)
    
    if not keyword_matches:
        # No matches - mark for review
        event.needs_review = True
        db.commit()
        return {
            "linked": 0,
            "needs_review": True,
            "reason": "No keyword matches found"
        }
    
    # Refine with numeric context
    refined_matches = refine_with_numeric_context(keyword_matches, numeric_values, db)
    
    # Calculate final confidences
    multiple_matches = len(refined_matches) > 1
    
    links_created = 0
    confidence_scores = []
    
    for code, base_conf, rationale, value in refined_matches:
        # Get signpost ID
        signpost = db.query(Signpost).filter(Signpost.code == code).first()
        if not signpost:
            continue
        
        # Calculate final confidence
        final_confidence = calculate_final_confidence(
            base_conf,
            has_numeric,
            multiple_matches,
            event.evidence_tier
        )
        
        # Policy: C/D tier NEVER moves gauges (set in link metadata via rationale)
        if event.evidence_tier in ("C", "D"):
            rationale += " [C/D tier: displayed but NEVER moves gauges]"
        
        # Create or update link
        existing_link = db.query(EventSignpostLink).filter(
            EventSignpostLink.event_id == event.id,
            EventSignpostLink.signpost_id == signpost.id
        ).first()
        
        if existing_link:
            existing_link.confidence = final_confidence
            existing_link.rationale = rationale
            existing_link.value = value
            existing_link.observed_at = event.published_at or event.ingested_at
        else:
            new_link = EventSignpostLink(
                event_id=event.id,
                signpost_id=signpost.id,
                confidence=final_confidence,
                rationale=rationale,
                value=value,
                observed_at=event.published_at or event.ingested_at
            )
            db.add(new_link)
        
        links_created += 1
        confidence_scores.append(final_confidence)
    
    # Determine if needs review
    max_confidence = max(confidence_scores) if confidence_scores else 0.0
    needs_review = max_confidence < 0.6
    
    event.needs_review = needs_review
    event.parsed = {
        **event.parsed or {},
        "mapped_at": datetime.now(timezone.utc).isoformat(),
        "max_confidence": max_confidence,
        "num_signposts": links_created
    }
    
    db.commit()
    
    return {
        "linked": links_created,
        "needs_review": needs_review,
        "max_confidence": max_confidence,
        "confidence_scores": confidence_scores
    }


def map_all_unmapped_events() -> Dict:
    """
    Map all events that don't have signpost links yet.
    
    Returns:
        Statistics dict
    """
    db = SessionLocal()
    stats = {
        "processed": 0,
        "linked": 0,
        "needs_review": 0,
        "unmapped": 0
    }
    
    try:
        # Find events without links
        events = db.query(Event).outerjoin(EventSignpostLink).filter(
            EventSignpostLink.event_id.is_(None)
        ).all()
        
        print(f"📍 Mapping {len(events)} unmapped events to signposts...")
        
        for event in events:
            result = map_event_to_signposts(event.id, db)
            stats["processed"] += 1
            
            if result.get("linked", 0) > 0:
                stats["linked"] += 1
                print(f"  ✓ Mapped: {event.title[:50]}... → {result['linked']} signposts (conf: {result.get('max_confidence', 0):.2f})")
            
            if result.get("needs_review"):
                stats["needs_review"] += 1
                print(f"  ⚠️  Needs review: {event.title[:50]}...")
            
            if result.get("linked", 0) == 0:
                stats["unmapped"] += 1
        
        print(f"\n✅ Mapping complete!")
        print(f"   Processed: {stats['processed']}")
        print(f"   Linked: {stats['linked']}")
        print(f"   Needs review: {stats['needs_review']}")
        print(f"   Unmapped: {stats['unmapped']}")
        
        return stats
    
    finally:
        db.close()

