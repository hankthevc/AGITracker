"""
Unit tests to verify HLE (Humanity's Last Exam) is monitor-only.

Confirms that HLE claims with first_class=False signposts do NOT affect:
- Overall composite gauge
- Capabilities category score
"""
import pytest
from datetime import datetime, timezone

from app.models import Benchmark, Claim, ClaimSignpost, Signpost, Source
from app.tasks.snap_index import compute_daily_snapshot


def test_hle_does_not_affect_composite(db_session):
    """
    Test that HLE claims (B-tier, first_class=False) do not move main gauges.
    
    Steps:
    1. Baseline: Compute index without HLE claims
    2. Add HLE claim with high score (≥70%)
    3. Recompute index
    4. Assert: Overall and Capabilities unchanged
    """
    # Create HLE benchmark
    hle_benchmark = Benchmark(
        code="humanitys_last_exam_text",
        name="Humanity's Last Exam (Text-Only)",
        url="https://scale.com/leaderboard/hle",
        family="OTHER"
    )
    db_session.add(hle_benchmark)
    
    # Create HLE signposts with first_class=False (monitor-only)
    hle_50 = Signpost(
        code="hle_text_50",
        name="HLE Text ≥50%",
        category="capabilities",
        metric_name="HLE Text Accuracy",
        baseline_value=20.0,
        target_value=50.0,
        unit="%",
        direction=">=",
        first_class=False,  # KEY: Monitor-only
    )
    hle_70 = Signpost(
        code="hle_text_70",
        name="HLE Text ≥70%",
        category="capabilities",
        metric_name="HLE Text Accuracy",
        baseline_value=20.0,
        target_value=70.0,
        unit="%",
        direction=">=",
        first_class=False,  # KEY: Monitor-only
    )
    db_session.add_all([hle_50, hle_70])
    db_session.commit()
    
    # Baseline snapshot (no HLE claims)
    baseline_result = compute_daily_snapshot()
    baseline_snapshots = db_session.execute(
        "SELECT overall, capabilities FROM index_snapshots ORDER BY snapshot_date DESC LIMIT 1"
    ).fetchone()
    
    if baseline_snapshots:
        baseline_overall = float(baseline_snapshots[0]) if baseline_snapshots[0] else 0.0
        baseline_capabilities = float(baseline_snapshots[1]) if baseline_snapshots[1] else 0.0
    else:
        baseline_overall = 0.0
        baseline_capabilities = 0.0
    
    print(f"\nBaseline - Overall: {baseline_overall}, Capabilities: {baseline_capabilities}")
    
    # Create B-tier source for HLE
    source = Source(
        url="https://scale.com/leaderboard/hle",
        domain="scale.com",
        source_type="leaderboard",
        credibility="B",  # Provisional
    )
    db_session.add(source)
    db_session.commit()
    
    # Add HLE claim with high score (75% - exceeds both signposts)
    hle_claim = Claim(
        title="HLE Text-Only: Test Model achieves 75%",
        summary="Test model scores 75% on HLE",
        metric_name="HLE Text Accuracy",
        metric_value=75.0,
        unit="%",
        observed_at=datetime.now(timezone.utc),
        source_id=source.id,
        url_hash="test_hle_75_percent",
        extraction_confidence=1.0,
    )
    db_session.add(hle_claim)
    db_session.commit()
    
    # Map claim to both HLE signposts
    for signpost in [hle_50, hle_70]:
        link = ClaimSignpost(
            claim_id=hle_claim.id,
            signpost_id=signpost.id,
            impact_estimate=1.0,  # Full impact on signpost
            fit_score=1.0,
        )
        db_session.add(link)
    db_session.commit()
    
    print(f"Added HLE claim: {hle_claim.metric_value}% (B-tier, first_class=False)")
    
    # Recompute after adding HLE claim
    recompute_result = compute_daily_snapshot()
    after_snapshots = db_session.execute(
        "SELECT overall, capabilities FROM index_snapshots ORDER BY snapshot_date DESC LIMIT 1"
    ).fetchone()
    
    if after_snapshots:
        after_overall = float(after_snapshots[0]) if after_snapshots[0] else 0.0
        after_capabilities = float(after_snapshots[1]) if after_snapshots[1] else 0.0
    else:
        after_overall = 0.0
        after_capabilities = 0.0
    
    print(f"After HLE - Overall: {after_overall}, Capabilities: {after_capabilities}")
    
    # ASSERTIONS: HLE should NOT affect gauges (monitor-only)
    assert after_overall == baseline_overall, \
        f"Overall gauge changed! {baseline_overall} → {after_overall}. HLE must be monitor-only."
    
    assert after_capabilities == baseline_capabilities, \
        f"Capabilities changed! {baseline_capabilities} → {after_capabilities}. HLE must be monitor-only."
    
    print("✓ HLE is monitor-only: gauges unchanged despite high-score claim")


def test_hle_signposts_marked_non_first_class(db_session):
    """Verify HLE signposts have first_class=False."""
    hle_signposts = db_session.query(Signpost).filter(
        Signpost.code.in_(["hle_text_50", "hle_text_70"])
    ).all()
    
    assert len(hle_signposts) >= 1, "HLE signposts should exist"
    
    for sp in hle_signposts:
        assert sp.first_class is False, \
            f"{sp.code} must have first_class=False (monitor-only)"
    
    print(f"✓ All {len(hle_signposts)} HLE signposts are first_class=False")

