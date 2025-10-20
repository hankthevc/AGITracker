#!/usr/bin/env python3
"""
Load signpost content from citations YAML into signpost_content table.

Populates why_matters, methodology, source papers, and technical explanations.
"""
import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "etl"))

from app.database import SessionLocal
from app.models import Signpost, SignpostContent


def load_content():
    """Load signpost content from citations YAML."""
    citations_path = Path(__file__).parent.parent / "infra" / "seeds" / "signpost_citations.yaml"
    
    if not citations_path.exists():
        print(f"❌ Citations file not found: {citations_path}")
        return 1
    
    with open(citations_path) as f:
        data = yaml.safe_load(f) or {}
    
    db = SessionLocal()
    stats = {"created": 0, "updated": 0, "skipped": 0}
    
    try:
        # Flatten all categories
        all_signposts = {}
        for category, signposts in data.items():
            if isinstance(signposts, dict):
                all_signposts.update(signposts)
        
        print(f"📚 Loading content for {len(all_signposts)} signposts...")
        
        for code, content_data in all_signposts.items():
            # Find signpost
            signpost = db.query(Signpost).filter(Signpost.code == code).first()
            if not signpost:
                print(f"  ⚠️  Signpost not found: {code}, skipping")
                stats["skipped"] += 1
                continue
            
            # Build key_papers JSON
            key_papers = []
            if content_data.get("source_paper"):
                key_papers.append({
                    "title": content_data["source_paper"],
                    "url": content_data.get("source_url", ""),
                    "citation": content_data.get("citation", ""),
                    "summary": content_data.get("methodology", "")
                })
            
            # Build current_state text
            current_state = f"Baseline: {content_data.get('baseline_sota', 'TBD')}\n"
            current_state += f"Target: {content_data.get('target_rationale', 'See methodology')}"
            
            # Build technical explanation
            technical = content_data.get("methodology", "")
            if content_data.get("quality_note"):
                technical += f"\n\n⚠️ Quality Note: {content_data['quality_note']}"
            
            # Check if content exists
            existing = db.query(SignpostContent).filter(
                SignpostContent.signpost_id == signpost.id
            ).first()
            
            if existing:
                # Update
                existing.why_matters = content_data.get("why_matters", "")
                existing.current_state = current_state
                existing.key_papers = key_papers
                existing.technical_explanation = technical
                stats["updated"] += 1
                action = "UPDATE"
            else:
                # Create
                new_content = SignpostContent(
                    signpost_id=signpost.id,
                    why_matters=content_data.get("why_matters", ""),
                    current_state=current_state,
                    key_papers=key_papers,
                    technical_explanation=technical
                )
                db.add(new_content)
                stats["created"] += 1
                action = "CREATE"
            
            print(f"  ✓ {action}: {code}")
        
        db.commit()
        
        print(f"\n✅ Content loading complete!")
        print(f"   Created: {stats['created']}, Updated: {stats['updated']}, Skipped: {stats['skipped']}")
        
        return 0
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        import traceback
        traceback.print_exc()
        return 1
    
    finally:
        db.close()


if __name__ == "__main__":
    sys.exit(load_content())
