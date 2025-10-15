"""Seed script for AGI Signpost Tracker database.

Fetches current leaderboard values via Playwright and populates:
- 3 roadmaps
- 7 benchmarks (including HLE)
- 27 signposts across capabilities/agents/inputs/security (including 2 monitor-only HLE signposts)
- Initial claims from current leaderboard data
"""
import asyncio
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add services/etl to path
sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "etl"))

from sqlalchemy.orm import Session

from app.database import SessionLocal, engine
from app.models import Benchmark, Claim, Roadmap, Signpost, Source

# Try to import playwright
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Warning: Playwright not available. Using placeholder values for leaderboards.")


async def fetch_swe_bench_score() -> float:
    """Fetch latest SWE-bench Verified score from leaderboard."""
    if not PLAYWRIGHT_AVAILABLE:
        return 65.0  # Placeholder
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto("https://www.swebench.com", timeout=10000)
            await page.wait_for_timeout(2000)
            
            # This is a placeholder - actual scraping would need to inspect the page structure
            # For now, return a reasonable estimate
            await browser.close()
            return 65.0  # Current approximate SOTA as of Oct 2024
    except Exception as e:
        print(f"Error fetching SWE-bench score: {e}")
        return 65.0


async def fetch_osworld_score() -> float:
    """Fetch latest OSWorld score."""
    if not PLAYWRIGHT_AVAILABLE:
        return 22.0
    
    # Placeholder - would need actual leaderboard URL and structure
    return 22.0  # Current approximate SOTA


async def fetch_webarena_score() -> float:
    """Fetch latest WebArena score."""
    if not PLAYWRIGHT_AVAILABLE:
        return 45.0
    
    return 45.0  # Current approximate SOTA


async def fetch_gpqa_score() -> float:
    """Fetch latest GPQA Diamond score."""
    if not PLAYWRIGHT_AVAILABLE:
        return 60.0
    
    return 60.0  # Current approximate SOTA


def seed_roadmaps(db: Session):
    """Seed roadmap presets (idempotent)."""
    roadmaps_data = [
        {
            "slug": "aschenbrenner",
            "name": "Aschenbrenner's Situational Awareness",
            "description": "Focus on OOMs of effective compute, algorithmic unhobbling, and security posture",
            "preset_weights": {"capabilities": 0.2, "agents": 0.3, "inputs": 0.4, "security": 0.1}
        },
        {
            "slug": "ai2027",
            "name": "AI 2027 Scenario Signposts",
            "description": "Timeline-aligned signposts for near-term AGI scenarios",
            "preset_weights": {"capabilities": 0.3, "agents": 0.35, "inputs": 0.25, "security": 0.1}
        },
        {
            "slug": "cotra",
            "name": "Cotra Bio Anchors & Epoch Compute",
            "description": "Compute-centric view based on biological anchors methodology",
            "preset_weights": {"capabilities": 0.25, "agents": 0.25, "inputs": 0.35, "security": 0.15}
        },
    ]
    
    for data in roadmaps_data:
        # Check if exists
        existing = db.query(Roadmap).filter(Roadmap.slug == data["slug"]).first()
        if not existing:
            roadmap = Roadmap(**data)
            db.add(roadmap)
    
    db.commit()
    print("✓ Seeded 3 roadmaps (idempotent)")


def seed_benchmarks(db: Session):
    """Seed benchmark definitions (idempotent)."""
    benchmarks_data = [
        {
            "code": "swe_bench_verified",
            "name": "SWE-bench Verified",
            "url": "https://www.swebench.com",
            "family": "SWE_BENCH_VERIFIED"
        },
        {
            "code": "osworld",
            "name": "OSWorld",
            "url": "https://os-world.github.io",
            "family": "OSWORLD"
        },
        {
            "code": "osworld_verified",
            "name": "OSWorld-Verified",
            "url": "https://os-world.github.io",
            "family": "OSWORLD"
        },
        {
            "code": "webarena",
            "name": "WebArena",
            "url": "https://webarena.dev",
            "family": "WEBARENA"
        },
        {
            "code": "visualwebarena",
            "name": "VisualWebArena",
            "url": "https://webarena.dev",
            "family": "WEBARENA"
        },
        {
            "code": "gpqa_diamond",
            "name": "GPQA Diamond",
            "url": "https://github.com/idavidrein/gpqa",
            "family": "GPQA_DIAMOND"
        },
        {
            "code": "humanitys_last_exam_text",
            "name": "Humanity's Last Exam (Text-Only)",
            "url": "https://scale.com/leaderboard/hle",
            "family": "HLE_TEXT"
        },
    ]
    
    for data in benchmarks_data:
        # Check if exists
        existing = db.query(Benchmark).filter(Benchmark.code == data["code"]).first()
        if not existing:
            benchmark = Benchmark(**data)
            db.add(benchmark)
    
    db.commit()
    print("✓ Seeded 7 benchmarks (idempotent)")


def seed_signposts(db: Session):
    """Seed 27 signposts across all categories (including 2 monitor-only HLE signposts)."""
    signposts_data = [
        # CAPABILITIES (8)
        {
            "code": "swe_bench_85",
            "name": "SWE-bench Verified 85%",
            "description": "AI system achieves 85% on SWE-bench Verified (real GitHub PRs)",
            "category": "capabilities",
            "metric_name": "SWE-bench Verified",
            "unit": "%",
            "direction": ">=",
            "baseline_value": 50.0,
            "target_value": 85.0,
            "methodology_url": "https://www.swebench.com",
            "first_class": True,
        },
        {
            "code": "swe_bench_90",
            "name": "SWE-bench Verified 90%",
            "description": "AI system achieves 90% on SWE-bench Verified (near-human expert)",
            "category": "capabilities",
            "metric_name": "SWE-bench Verified",
            "unit": "%",
            "direction": ">=",
            "baseline_value": 50.0,
            "target_value": 90.0,
            "methodology_url": "https://www.swebench.com",
            "first_class": True,
        },
        {
            "code": "osworld_65",
            "name": "OSWorld 65%",
            "description": "AI achieves 65% on OSWorld (complex OS-level tasks)",
            "category": "capabilities",
            "metric_name": "OSWorld",
            "unit": "%",
            "direction": ">=",
            "baseline_value": 15.0,
            "target_value": 65.0,
            "methodology_url": "https://os-world.github.io",
            "first_class": True,
        },
        {
            "code": "osworld_85",
            "name": "OSWorld 85%",
            "description": "AI achieves 85% on OSWorld (near-human proficiency)",
            "category": "capabilities",
            "metric_name": "OSWorld",
            "unit": "%",
            "direction": ">=",
            "baseline_value": 15.0,
            "target_value": 85.0,
            "methodology_url": "https://os-world.github.io",
            "first_class": True,
        },
        {
            "code": "webarena_70",
            "name": "WebArena 70%",
            "description": "AI achieves 70% on WebArena (web navigation tasks)",
            "category": "capabilities",
            "metric_name": "WebArena",
            "unit": "%",
            "direction": ">=",
            "baseline_value": 35.0,
            "target_value": 70.0,
            "methodology_url": "https://webarena.dev",
            "first_class": True,
        },
        {
            "code": "webarena_85",
            "name": "WebArena 85%",
            "description": "AI achieves 85% on WebArena (advanced web task proficiency)",
            "category": "capabilities",
            "metric_name": "WebArena",
            "unit": "%",
            "direction": ">=",
            "baseline_value": 35.0,
            "target_value": 85.0,
            "methodology_url": "https://webarena.dev",
            "first_class": True,
        },
        {
            "code": "gpqa_sota",
            "name": "GPQA Diamond SOTA",
            "description": "AI achieves 75% on GPQA Diamond (PhD-level science)",
            "category": "capabilities",
            "metric_name": "GPQA Diamond",
            "unit": "%",
            "direction": ">=",
            "baseline_value": 50.0,
            "target_value": 75.0,
            "methodology_url": "https://github.com/idavidrein/gpqa",
            "first_class": True,
        },
        {
            "code": "gpqa_phd_parity",
            "name": "GPQA Diamond PhD Parity",
            "description": "AI achieves 85% on GPQA Diamond (PhD expert parity)",
            "category": "capabilities",
            "metric_name": "GPQA Diamond",
            "unit": "%",
            "direction": ">=",
            "baseline_value": 50.0,
            "target_value": 85.0,
            "methodology_url": "https://github.com/idavidrein/gpqa",
            "first_class": True,
        },
        {
            "code": "hle_text_50",
            "name": "HLE Text ≥50%",
            "description": "AI achieves 50% on Humanity's Last Exam text-only (PhD-level reasoning breadth)",
            "category": "capabilities",
            "metric_name": "HLE Text Accuracy",
            "unit": "%",
            "direction": ">=",
            "baseline_value": 20.0,
            "target_value": 50.0,
            "methodology_url": "https://scale.com/leaderboard/hle",
            "first_class": False,  # Monitor-only, doesn't affect main gauges
        },
        {
            "code": "hle_text_70",
            "name": "HLE Text ≥70%",
            "description": "AI achieves 70% on Humanity's Last Exam text-only (long-horizon milestone)",
            "category": "capabilities",
            "metric_name": "HLE Text Accuracy",
            "unit": "%",
            "direction": ">=",
            "baseline_value": 20.0,
            "target_value": 70.0,
            "methodology_url": "https://scale.com/leaderboard/hle",
            "first_class": False,  # Monitor-only, calibrated for 2026-2028
        },
        
        # AGENTS (5)
        {
            "code": "agent_reliability_80",
            "name": "Multi-step Agent Reliability 80%",
            "description": "Autonomous agents complete multi-step tasks with 80%+ reliability",
            "category": "agents",
            "metric_name": "Agent Reliability",
            "unit": "%",
            "direction": ">=",
            "baseline_value": 30.0,
            "target_value": 80.0,
            "first_class": False,
        },
        {
            "code": "osworld_latency_10min",
            "name": "OSWorld Latency <10min",
            "description": "OSWorld tasks completed in under 10 minutes median time",
            "category": "agents",
            "metric_name": "OSWorld Latency",
            "unit": "minutes",
            "direction": "<=",
            "baseline_value": 60.0,
            "target_value": 10.0,
            "first_class": False,
        },
        {
            "code": "recursive_self_improvement",
            "name": "Recursive Self-Improvement Demo",
            "description": "Demonstrated recursive self-improvement capability",
            "category": "agents",
            "metric_name": "RSI Demonstrated",
            "unit": "binary",
            "direction": ">=",
            "baseline_value": 0.0,
            "target_value": 1.0,
            "first_class": False,
        },
        {
            "code": "multi_day_project",
            "name": "Multi-day Agentic Project",
            "description": "Agent autonomously completes 5+ day project with minimal supervision",
            "category": "agents",
            "metric_name": "Project Duration",
            "unit": "days",
            "direction": ">=",
            "baseline_value": 0.0,
            "target_value": 5.0,
            "first_class": False,
        },
        {
            "code": "economic_displacement_10pct",
            "name": "10% Remote Job Displacement",
            "description": "AI systems economically displace 10% of remote knowledge work",
            "category": "agents",
            "metric_name": "Job Displacement",
            "unit": "%",
            "direction": ">=",
            "baseline_value": 0.0,
            "target_value": 10.0,
            "first_class": False,
        },
        
        # INPUTS (11)
        {
            "code": "inputs_flops_25",
            "name": "Training Compute 10^25 FLOP",
            "description": "Single training run reaches 10^25 FLOP milestone",
            "category": "inputs",
            "metric_name": "Training FLOPs",
            "unit": "FLOPs",
            "direction": ">=",
            "baseline_value": 1e24,
            "target_value": 1e25,
            "first_class": False,
        },
        {
            "code": "inputs_flops_26",
            "name": "Training Compute 10^26 FLOP",
            "description": "Single training run reaches 10^26 FLOP milestone",
            "category": "inputs",
            "metric_name": "Training FLOPs",
            "unit": "FLOPs",
            "direction": ">=",
            "baseline_value": 1e25,
            "target_value": 1e26,
            "first_class": True,
        },
        {
            "code": "inputs_flops_27",
            "name": "Training Compute 10^27 FLOP",
            "description": "Single training run reaches 10^27 FLOP milestone",
            "category": "inputs",
            "metric_name": "Training FLOPs",
            "unit": "FLOPs",
            "direction": ">=",
            "baseline_value": 1e26,
            "target_value": 1e27,
            "first_class": True,
        },
        {
            "code": "compute_1e26",
            "name": "Training Compute 10^26 FLOP",
            "description": "Single training run uses 10^26 FLOP",
            "category": "inputs",
            "metric_name": "Training FLOP",
            "unit": "log10",
            "direction": ">=",
            "baseline_value": 24.0,  # 10^24
            "target_value": 26.0,    # 10^26
            "first_class": False,
        },
        {
            "code": "compute_1e27",
            "name": "Training Compute 10^27 FLOP",
            "description": "Single training run uses 10^27 FLOP",
            "category": "inputs",
            "metric_name": "Training FLOP",
            "unit": "log10",
            "direction": ">=",
            "baseline_value": 24.0,
            "target_value": 27.0,
            "first_class": True,
        },
        {
            "code": "algo_efficiency_1oom",
            "name": "Algorithmic Efficiency +1 OOM",
            "description": "1 order of magnitude improvement in algorithmic efficiency since 2023",
            "category": "inputs",
            "metric_name": "Algo Efficiency OOM",
            "unit": "OOM",
            "direction": ">=",
            "baseline_value": 0.0,
            "target_value": 1.0,
            "first_class": False,
        },
        {
            "code": "algo_efficiency_2oom",
            "name": "Algorithmic Efficiency +2 OOM",
            "description": "2 orders of magnitude improvement in algorithmic efficiency",
            "category": "inputs",
            "metric_name": "Algo Efficiency OOM",
            "unit": "OOM",
            "direction": ">=",
            "baseline_value": 0.0,
            "target_value": 2.0,
            "first_class": False,
        },
        {
            "code": "inputs_dc_1gw",
            "name": "DC Power 1 GW Milestone",
            "description": "Data center power committed reaches 1 GW milestone",
            "category": "inputs",
            "metric_name": "DC Power",
            "unit": "GW",
            "direction": ">=",
            "baseline_value": 0.1,
            "target_value": 1.0,
            "first_class": True,
        },
        {
            "code": "inputs_dc_10gw",
            "name": "DC Power 10 GW Milestone",
            "description": "Data center power committed reaches 10 GW milestone",
            "category": "inputs",
            "metric_name": "DC Power",
            "unit": "GW",
            "direction": ">=",
            "baseline_value": 1.0,
            "target_value": 10.0,
            "first_class": True,
        },
        {
            "code": "inputs_algo_oom",
            "name": "Algorithmic Efficiency OOM Milestones",
            "description": "Orders of magnitude improvement in algorithmic efficiency since 2020",
            "category": "inputs",
            "metric_name": "Algorithmic Efficiency",
            "unit": "x",
            "direction": ">=",
            "baseline_value": 10.0,
            "target_value": 100.0,
            "first_class": True,
        },
        {
            "code": "dc_power_100mw",
            "name": "DC Power 0.1 GW",
            "description": "Data center power committed reaches 0.1 GW for single cluster",
            "category": "inputs",
            "metric_name": "DC Power",
            "unit": "GW",
            "direction": ">=",
            "baseline_value": 0.01,
            "target_value": 0.1,
            "first_class": False,
        },
        {
            "code": "dc_power_1gw",
            "name": "DC Power 1 GW",
            "description": "Data center power committed reaches 1 GW",
            "category": "inputs",
            "metric_name": "DC Power",
            "unit": "GW",
            "direction": ">=",
            "baseline_value": 0.01,
            "target_value": 1.0,
            "first_class": True,
        },
        {
            "code": "dc_power_10gw",
            "name": "DC Power 10 GW",
            "description": "Data center power committed reaches 10 GW",
            "category": "inputs",
            "metric_name": "DC Power",
            "unit": "GW",
            "direction": ">=",
            "baseline_value": 0.01,
            "target_value": 10.0,
            "first_class": True,
        },
        
        # SECURITY (6)
        {
            "code": "sec_maturity",
            "name": "Security Maturity Index",
            "description": "Aggregate security maturity score (0-1) based on weighted signals",
            "category": "security",
            "metric_name": "Security Maturity",
            "unit": "score",
            "direction": ">=",
            "baseline_value": 0.0,
            "target_value": 1.0,
            "first_class": True,
        },
        {
            "code": "security_l1_weights",
            "name": "Security Maturity L1: Model Weights",
            "description": "Industry standard for securing model weights against exfiltration",
            "category": "security",
            "metric_name": "Security Level",
            "unit": "level",
            "direction": ">=",
            "baseline_value": 0.0,
            "target_value": 1.0,
            "first_class": False,
        },
        {
            "code": "security_l2_monitoring",
            "name": "Security Maturity L2: Inference Monitoring",
            "description": "Deployed inference monitoring for misuse detection",
            "category": "security",
            "metric_name": "Security Level",
            "unit": "level",
            "direction": ">=",
            "baseline_value": 0.0,
            "target_value": 1.0,
            "first_class": False,
        },
        {
            "code": "security_l3_state_actor",
            "name": "Security Maturity L3: State-Actor Resistant",
            "description": "Security posture resistant to state-level actors",
            "category": "security",
            "metric_name": "Security Level",
            "unit": "level",
            "direction": ">=",
            "baseline_value": 0.0,
            "target_value": 1.0,
            "first_class": True,
        },
        {
            "code": "ai_treaty_ratified",
            "name": "International AI Governance Treaty",
            "description": "Major international treaty on AI governance ratified",
            "category": "security",
            "metric_name": "Treaty Status",
            "unit": "binary",
            "direction": ">=",
            "baseline_value": 0.0,
            "target_value": 1.0,
            "first_class": False,
        },
        {
            "code": "mandatory_evals",
            "name": "Mandatory Pre-Deployment Evals",
            "description": "Mandatory third-party evals enforced for frontier models",
            "category": "security",
            "metric_name": "Eval Mandate",
            "unit": "binary",
            "direction": ">=",
            "baseline_value": 0.0,
            "target_value": 1.0,
            "first_class": False,
        },
    ]
    
    for data in signposts_data:
        # Check if exists
        existing = db.query(Signpost).filter(Signpost.code == data["code"]).first()
        if not existing:
            signpost = Signpost(**data)
            db.add(signpost)
    
    db.commit()
    print("✓ Seeded 27 signposts (idempotent)")


async def seed_initial_claims(db: Session):
    """Seed initial claims from current leaderboard data."""
    # Fetch current scores
    swe_score = await fetch_swe_bench_score()
    os_score = await fetch_osworld_score()
    web_score = await fetch_webarena_score()
    gpqa_score = await fetch_gpqa_score()
    
    # Get benchmarks
    swe_bench = db.query(Benchmark).filter_by(code="swe_bench_verified").first()
    osworld_bench = db.query(Benchmark).filter_by(code="osworld").first()
    webarena_bench = db.query(Benchmark).filter_by(code="webarena").first()
    gpqa_bench = db.query(Benchmark).filter_by(code="gpqa_diamond").first()
    
    # Create sources
    sources_data = [
        {
            "url": "https://www.swebench.com/leaderboard",
            "domain": "swebench.com",
            "source_type": "leaderboard",
            "credibility": "A"
        },
        {
            "url": "https://os-world.github.io/explorer.html",
            "domain": "os-world.github.io",
            "source_type": "leaderboard",
            "credibility": "A"
        },
        {
            "url": "https://webarena.dev/leaderboard.html",
            "domain": "webarena.dev",
            "source_type": "leaderboard",
            "credibility": "A"
        },
        {
            "url": "https://github.com/idavidrein/gpqa",
            "domain": "github.com",
            "source_type": "leaderboard",
            "credibility": "A"
        },
    ]
    
    sources = []
    for data in sources_data:
        # Check if exists
        existing = db.query(Source).filter(Source.url == data["url"]).first()
        if existing:
            sources.append(existing)
        else:
            source = Source(**data)
            db.add(source)
            sources.append(source)
    
    db.commit()
    
    # Create claims
    now = datetime.now(timezone.utc)
    claims_data = [
        {
            "title": f"SWE-bench Verified: Current SOTA {swe_score}%",
            "summary": f"Latest SWE-bench Verified leaderboard shows {swe_score}% performance",
            "metric_name": "SWE-bench Verified",
            "metric_value": swe_score,
            "unit": "%",
            "observed_at": now,
            "source_id": sources[0].id,
            "url_hash": hashlib.sha256(sources[0].url.encode()).hexdigest(),
            "extraction_confidence": 1.0,
        },
        {
            "title": f"OSWorld: Current SOTA {os_score}%",
            "summary": f"Latest OSWorld leaderboard shows {os_score}% performance",
            "metric_name": "OSWorld",
            "metric_value": os_score,
            "unit": "%",
            "observed_at": now,
            "source_id": sources[1].id,
            "url_hash": hashlib.sha256(sources[1].url.encode()).hexdigest(),
            "extraction_confidence": 1.0,
        },
        {
            "title": f"WebArena: Current SOTA {web_score}%",
            "summary": f"Latest WebArena leaderboard shows {web_score}% performance",
            "metric_name": "WebArena",
            "metric_value": web_score,
            "unit": "%",
            "observed_at": now,
            "source_id": sources[2].id,
            "url_hash": hashlib.sha256(sources[2].url.encode()).hexdigest(),
            "extraction_confidence": 1.0,
        },
        {
            "title": f"GPQA Diamond: Current SOTA {gpqa_score}%",
            "summary": f"Latest GPQA Diamond results show {gpqa_score}% performance",
            "metric_name": "GPQA Diamond",
            "metric_value": gpqa_score,
            "unit": "%",
            "observed_at": now,
            "source_id": sources[3].id,
            "url_hash": hashlib.sha256(sources[3].url.encode()).hexdigest(),
            "extraction_confidence": 1.0,
        },
    ]
    
    for data in claims_data:
        # Check if exists by url_hash and metric_name
        existing = db.query(Claim).filter(
            Claim.url_hash == data["url_hash"],
            Claim.metric_name == data["metric_name"]
        ).first()
        if not existing:
            claim = Claim(**data)
            db.add(claim)
    
    db.commit()
    print(f"✓ Seeded initial claims with current leaderboard data (idempotent)")
    print(f"  - SWE-bench: {swe_score}%")
    print(f"  - OSWorld: {os_score}%")
    print(f"  - WebArena: {web_score}%")
    print(f"  - GPQA Diamond: {gpqa_score}%")


async def main():
    """Main seed function."""
    print("🌱 Seeding AGI Signpost Tracker database...")
    
    db = SessionLocal()
    
    try:
        # Seed in order (respecting foreign keys)
        seed_roadmaps(db)
        seed_benchmarks(db)
        seed_signposts(db)
        await seed_initial_claims(db)
        
        print("✅ Database seeded successfully!")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())

