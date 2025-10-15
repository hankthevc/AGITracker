"""GPQA-Diamond leaderboard scraper."""
import asyncio
import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Dict, List

from celery import shared_task
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeout

from app.celery_app import celery_app
from app.database import SessionLocal
from app.models import Claim, ClaimSignpost, Source, Signpost


async def fetch_gpqa_leaderboard() -> Optional[List[Dict]]:
    """
    Fetch GPQA-Diamond leaderboard from Artificial Analysis.
    
    Returns list of entries with model, accuracy, date.
    Note: Marked as B-tier unless backed by paper/model card link.
    """
    print("🔍 Fetching GPQA-Diamond from artificialanalysis.ai...")
    
    # Check if we should scrape real data
    scrape_real = os.getenv("SCRAPE_REAL", "false").lower() == "true"
    
    if not scrape_real:
        print("⚠️  SCRAPE_REAL=false, using cached fixture if available")
        cache_dir = Path(__file__).parent.parent.parent.parent.parent / "infra" / "cache"
        cache_files = sorted(cache_dir.glob("gpqa_*.html"), reverse=True)
        if cache_files:
            print(f"✓ Using cached fixture: {cache_files[0]}")
            # In production, parse the cached HTML here
            return []
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Navigate to GPQA-Diamond evaluation page
            await page.goto("https://artificialanalysis.ai/evaluations/gpqa-diamond", timeout=30000)
            await page.wait_for_load_state("networkidle", timeout=15000)
            
            # Cache HTML snapshot
            cache_dir = Path(__file__).parent.parent.parent.parent.parent / "infra" / "cache"
            cache_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            cache_file = cache_dir / f"gpqa_{timestamp}.html"
            
            html = await page.content()
            with open(cache_file, "w", encoding="utf-8") as f:
                f.write(html)
            
            print(f"✓ Cached HTML to {cache_file}")
            
            # Parse leaderboard
            results = []
            
            # Look for table or card-based layout
            # Artificial Analysis uses a custom layout, try multiple strategies
            
            # Strategy 1: Look for table
            tables = page.locator('table')
            table_count = await tables.count()
            print(f"Found {table_count} tables")
            
            if table_count > 0:
                table = tables.first
                rows = table.locator('tbody tr, tr')
                row_count = await rows.count()
                print(f"Table has {row_count} rows")
                
                for i in range(min(row_count, 15)):  # Top 15 models
                    row = rows.nth(i)
                    cells = row.locator('td, th')
                    cell_count = await cells.count()
                    
                    if cell_count >= 2:
                        model_name = await cells.nth(0).text_content()
                        score_text = await cells.nth(1).text_content()
                        
                        try:
                            # Extract percentage (e.g., "75.3%" -> 75.3 or "0.753" -> 75.3)
                            score_clean = score_text.strip().replace('%', '')
                            score = float(score_clean)
                            
                            # Convert to percentage if decimal
                            if score < 1.0:
                                score = score * 100
                            
                            # Check if this entry has a paper link (makes it A-tier)
                            row_html = await row.inner_html()
                            has_paper_link = 'arxiv.org' in row_html or 'paper' in row_html.lower()
                            credibility = 'A' if has_paper_link else 'B'
                            
                            results.append({
                                'model_name': model_name.strip(),
                                'accuracy': score,
                                'metric_name': 'Accuracy',
                                'date': datetime.now(timezone.utc),
                                'credibility': credibility,
                                'has_paper': has_paper_link,
                            })
                            print(f"  ✓ Parsed: {model_name.strip()} = {score}% (tier {credibility})")
                        except (ValueError, AttributeError) as e:
                            print(f"  ⚠️  Could not parse score from '{score_text}': {e}")
            
            # Strategy 2: Look for divs/cards (if table parsing failed)
            if not results:
                print("⚠️  Table parsing yielded no results, trying card layout...")
                cards = page.locator('[data-model], .model-card, div[class*="model"]')
                card_count = await cards.count()
                print(f"Found {card_count} potential model cards")
                
                # This would need custom parsing based on actual HTML structure
                # For now, log a warning
                if card_count > 0:
                    print("⚠️  Card-based layout detected but parser not implemented")
            
            await browser.close()
            
            if not results:
                print("⚠️  No results parsed - HTML structure may have changed")
                return None
            
            return results
            
    except PlaywrightTimeout as e:
        print(f"❌ Timeout fetching GPQA: {e}")
        return None
    except Exception as e:
        print(f"❌ Error fetching GPQA: {e}")
        return None


def create_or_update_claim(db, source: Source, data: Dict) -> Optional[Claim]:
    """Create or update a claim from GPQA data."""
    
    # Create unique hash
    claim_hash_input = (
        f"{source.url}:{data['model_name']}:{data['metric_name']}:"
        f"{data['accuracy']}:{data['date'].date().isoformat()}"
    )
    url_hash = hashlib.sha256(claim_hash_input.encode()).hexdigest()[:16]
    
    # Check if exists
    existing = db.query(Claim).filter(Claim.url_hash == url_hash).first()
    if existing:
        print(f"  ↻ Claim already exists: {data['model_name']} = {data['accuracy']}%")
        return existing
    
    # Create new claim
    claim = Claim(
        url_hash=url_hash,
        source_id=source.id,
        title=f"{data['model_name']} achieves {data['accuracy']}% accuracy on GPQA-Diamond",
        body=f"Model: {data['model_name']}, Accuracy: {data['accuracy']}%, Benchmark: GPQA-Diamond. {'Backed by paper.' if data.get('has_paper') else 'From leaderboard (provisional).'}",
        metric_name=data['metric_name'],
        metric_value=data['accuracy'],
        unit='%',
        observed_at=data['date'],
        retracted=False,
    )
    db.add(claim)
    db.flush()
    
    print(f"  ✓ Created claim ID {claim.id}: {data['model_name']} = {data['accuracy']}% (tier {data['credibility']})")
    return claim


@shared_task(bind=True, name='fetch_gpqa')
def fetch_gpqa(self):
    """
    Celery task to fetch GPQA-Diamond leaderboard data.
    
    Scrapes artificialanalysis.ai for GPQA-Diamond accuracy scores.
    Creates claims with tier B by default (leaderboard), A if backed by paper.
    
    Note: B-tier evidence shows as "provisional" in UI and does NOT move main gauges.
    """
    print("\n" + "="*60)
    print("🌐 Starting GPQA-Diamond leaderboard fetch")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # Get or create source
        source_url = "https://artificialanalysis.ai/evaluations/gpqa-diamond"
        source = db.query(Source).filter(Source.url == source_url).first()
        
        if not source:
            source = Source(
                url=source_url,
                domain="artificialanalysis.ai",
                source_type="leaderboard",
                credibility="B",  # Leaderboard = B-tier by default
            )
            db.add(source)
            db.flush()
            print(f"✓ Created source: {source_url} (tier B)")
        else:
            print(f"✓ Using existing source ID {source.id}")
        
        # Fetch leaderboard data
        loop = asyncio.get_event_loop()
        results = loop.run_until_complete(fetch_gpqa_leaderboard())
        
        if not results:
            print("⚠️  No results to process")
            return {"status": "no_data", "claims_created": 0}
        
        print(f"\n📊 Processing {len(results)} results...")
        
        claims_created = 0
        signposts_mapped = set()
        
        for data in results:
            # Create or update source based on credibility
            # If this result has a paper link, upgrade to A-tier source
            if data.get('has_paper') and data['credibility'] == 'A':
                # Create separate A-tier source for this paper-backed result
                paper_source = Source(
                    url=f"{source_url}#{data['model_name']}",
                    domain="artificialanalysis.ai",
                    source_type="paper",
                    credibility="A",
                )
                db.add(paper_source)
                db.flush()
                current_source = paper_source
            else:
                current_source = source
            
            # Create claim
            claim = create_or_update_claim(db, current_source, data)
            if not claim:
                continue
            
            claims_created += 1
            
            # Map to signposts based on accuracy thresholds
            # gpqa_sota: 75% accuracy (Capabilities - PhD-level reasoning)
            # gpqa_phd_parity: 85% accuracy (Capabilities - PhD expert parity)
            accuracy = data['accuracy']
            
            signpost_mappings = []
            if accuracy >= 75:
                signpost_mappings.append(('gpqa_sota', 'capabilities', 0.08))
            if accuracy >= 85:
                signpost_mappings.append(('gpqa_phd_parity', 'capabilities', 0.12))
            
            for signpost_code, category, contribution in signpost_mappings:
                signpost = db.query(Signpost).filter(Signpost.code == signpost_code).first()
                if signpost:
                    # Check if mapping exists
                    existing_mapping = db.query(ClaimSignpost).filter(
                        ClaimSignpost.claim_id == claim.id,
                        ClaimSignpost.signpost_id == signpost.id
                    ).first()
                    
                    if not existing_mapping:
                        claim_signpost = ClaimSignpost(
                            claim_id=claim.id,
                            signpost_id=signpost.id,
                            score_contribution=contribution,
                            mapped_via='rule',
                        )
                        db.add(claim_signpost)
                        signposts_mapped.add(signpost_code)
                        print(f"  ✓ Mapped to signpost: {signpost_code}")
        
        db.commit()
        
        # Trigger snapshot recomputation if claims created
        if claims_created > 0:
            print(f"\n✅ Created {claims_created} claims, mapped to {len(signposts_mapped)} signposts")
            print("ℹ️  Note: B-tier claims show as 'provisional' and do NOT move main gauges")
            print("🔄 Triggering snapshot recomputation...")
            
            from app.tasks.snap_index import compute_daily_snapshot
            compute_daily_snapshot.delay()
        
        return {
            "status": "success",
            "claims_created": claims_created,
            "signposts_mapped": list(signposts_mapped),
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error in fetch_gpqa: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    # For testing
    fetch_gpqa()

