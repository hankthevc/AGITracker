"""Write human pace analyses for signpost + roadmap combinations."""
import sys
from pathlib import Path

# Add services/etl to path
sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "etl"))

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import PaceAnalysis, Roadmap, Signpost


PACE_ANALYSES = {
    # SWE-bench + Aschenbrenner
    ("swe_bench_85", "aschenbrenner"): """We are approximately 2-3 months ahead of Aschenbrenner's projected pace. His timeline assumed gradual unhobbling gains plus steady compute scaling would reach 85% by late 2025/early 2026.

The faster-than-expected progress appears driven by:
1. Chain-of-thought reasoning breakthroughs (o1-preview, Claude 4.5 thinking protocols)
2. Larger context windows enabling better repository understanding
3. Compound effects of test-driven iteration

If this pace continues, we could see 85%+ by mid-2025, a 6-month acceleration. This would validate Aschenbrenner's core thesis about rapid capability gains but suggest algorithmic unhobbling is happening faster than his conservative estimates.

Critical to watch: Whether progress continues linearly or hits a plateau around 75-80% as tasks require deeper reasoning and domain expertise.""",
    
    # SWE-bench + AI 2027
    ("swe_bench_85", "ai2027"): """We are roughly on track with AI 2027's baseline scenario. The 70.6% achievement in Oct 2024 aligns well with the predicted 70% by mid-2025 milestone.

Current trajectory suggests 85% by late 2026 is achievable, matching the scenario's timeline. The key question is whether we'll see:
- Continued linear progress (current ~20% gain per year)
- Acceleration from algorithmic breakthroughs
- Plateau as easy gains are exhausted

If acceleration continues, we could beat the timeline by 6-12 months, potentially reaching 85% by mid-2026 instead of late 2026.""",
    
    # SWE-bench + Cotra
    ("swe_bench_85", "cotra"): """Cotra's bio anchors framework focuses more on compute scaling than specific capability milestones. The rapid SWE-bench progress with relatively modest compute increases (10^24-10^25 FLOPs training runs) suggests:

1. Algorithmic efficiency is advancing faster than compute-only models predicted
2. The 'effective compute' multiplier from better algorithms is larger than conservative estimates
3. Code generation may be an easier domain than general reasoning (rich training signal from GitHub)

This ahead-of-schedule progress on a specific benchmark doesn't necessarily mean we're ahead on the path to transformative AI—but it does suggest the compute requirements might be lower than biological anchor estimates.""",
    
    # OSWorld + Aschenbrenner
    ("osworld_50", "aschenbrenner"): """We appear to be 12-18 months behind Aschenbrenner's implicit timeline for agent capabilities. With current progress at ~22-25%, reaching 50% by his implied 2026 target requires ~2x annual improvement.

The slower progress here vs SWE-bench reveals that:
- Visual-motor control is harder than text-based reasoning
- Multi-step agent workflows remain a bottleneck
- Tool use and error recovery need more work

To catch up to Aschenbrenner's timeline, we'd need either:
- Major architectural breakthroughs in visual reasoning
- Better training data from human computer use demonstrations
- Improved long-horizon planning capabilities

The gap here is more concerning than SWE-bench because autonomous agents are central to his 'drop-in remote worker' vision.""",
    
    # OSWorld + AI 2027
    ("osworld_50", "ai2027"): """We are significantly behind the AI 2027 scenario timeline, which predicted 50% by 2026. At current ~22% with 14 months to go, we'd need ~2.3x improvement—historically unprecedented for this benchmark.

The slower-than-expected progress suggests:
- Computer use is genuinely hard (not just a data problem)
- Vision + action integration needs fundamental advances
- Current architectures may not scale smoothly to agent tasks

To get back on track would require:
- Breakthrough in visual understanding of GUIs
- New training paradigms for multi-step planning
- Better sim-to-real transfer for computer use

If we don't see acceleration soon, the 2027 timeline for autonomous digital workers looks optimistic.""",
    
    # OSWorld + Cotra
    ("osworld_70", "cotra"): """The OSWorld benchmark doesn't map cleanly to Cotra's compute-centric framework, but the slow progress is notable. We're seeing strong returns to compute scaling on text tasks (SWE-bench, GPQA) but much weaker returns on computer use.

This suggests:
- Compute scaling alone won't solve agent capabilities
- Need algorithmic/architectural innovations beyond pure scale
- The 'general intelligence' threshold may require solving multi-modal control, not just text reasoning

For bio anchors adherents, this is mildly concerning—it suggests the path to transformative AI involves solving harder problems than just 'more compute on better algorithms.'""",
    
    # WebArena + Aschenbrenner
    ("webarena_60", "aschenbrenner"): """WebArena progress at ~45% puts us roughly 6-9 months behind Aschenbrenner's implicit agent timeline. While better than OSWorld, it still reveals gaps in sustained multi-page workflows.

The challenge: web navigation requires combining vision, planning, and error recovery—all areas where current models are weakest. To hit 60% by 2026 requires:
- Better handling of dynamic JavaScript-heavy sites
- Improved session/state management
- More robust error recovery

The good news: web tasks are more tractable than full OS control, so we might see faster progress once the core agent infrastructure improves.""",
    
    # WebArena + AI 2027
    ("webarena_60", "ai2027"): """Current 45% vs predicted 60% by 2026 means we need ~33% relative improvement in 14 months—challenging but not impossible given recent progress.

The key is whether improvements in vision models and planning algorithms transfer to web navigation. If so, we could see rapid gains. If not, we may hit a plateau.

Watch for: Better handling of auth flows, improved form filling accuracy, more reliable multi-site workflows.""",
    
    # WebArena + Cotra
    ("webarena_80", "cotra"): """Web navigation progress doesn't directly inform Cotra's compute-scaling models, but it does test a key assumption: whether throwing more compute at foundation models will naturally yield agent capabilities.

So far, the answer is 'partially'—we see gains but not smooth scaling. This suggests agent capabilities may require dedicated training regimes (RL on web tasks, demonstrations, etc.) rather than emerging naturally from scale.""",
    
    # GPQA + Aschenbrenner
    ("gpqa_75", "aschenbrenner"): """At ~60-67% vs human expert 75%, we're close to Aschenbrenner's assumed reasoning capabilities for his timeline. The o1-preview achievement of 67% via RL on reasoning suggests we might hit 75% by mid-2025.

This matters because scientific reasoning is a proxy for 'true' general intelligence—not just pattern matching but genuine problem-solving. Reaching human parity here would be a major milestone.

The question: does RL on chain-of-thought continue to scale, or do we need fundamental new approaches to crack the last 15%?""",
    
    # GPQA + AI 2027
    ("gpqa_75", "ai2027"): """We're roughly on track with AI 2027's reasoning timeline. Current ~60-67% with 14 months to 75% target requires ~15-25% relative improvement—achievable if recent RL advances continue.

The concern: gains from o1-preview may represent 'low-hanging fruit' from better reasoning training. Reaching true human expert level (85%) might require qualitative leaps, not just better training.""",
    
    # GPQA + Cotra
    ("gpqa_85", "cotra"): """Scientific reasoning progress aligns reasonably well with Cotra's model—steady gains from larger models and better training. The jump from o1-preview shows that algorithmic improvements (RL on reasoning) do provide meaningful boosts.

If gains continue, we might see human parity (75%) with 10^25-10^26 FLOP models, and superhuman (85%+) with 10^27 FLOPs—consistent with bio anchors estimates for transformative AI.""",
}


def seed_pace_analyses():
    """Seed pace analysis texts into database."""
    
    db = SessionLocal()
    try:
        # Get signposts and roadmaps
        signposts = {s.code: s for s in db.query(Signpost).all()}
        roadmaps = {r.slug: r for r in db.query(Roadmap).all()}
        
        inserted_count = 0
        for (signpost_code, roadmap_slug), analysis_text in PACE_ANALYSES.items():
            signpost = signposts.get(signpost_code)
            roadmap = roadmaps.get(roadmap_slug)
            
            if not signpost or not roadmap:
                print(f"Warning: {signpost_code} or {roadmap_slug} not found")
                continue
            
            # Check if analysis already exists
            existing = db.query(PaceAnalysis).filter_by(
                signpost_id=signpost.id,
                roadmap_id=roadmap.id
            ).first()
            
            if not existing:
                analysis = PaceAnalysis(
                    signpost_id=signpost.id,
                    roadmap_id=roadmap.id,
                    analysis_text=analysis_text
                )
                db.add(analysis)
                inserted_count += 1
        
        db.commit()
        print(f"✓ Inserted {inserted_count} pace analyses")
        
    except Exception as e:
        print(f"Error seeding pace analyses: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_pace_analyses()

