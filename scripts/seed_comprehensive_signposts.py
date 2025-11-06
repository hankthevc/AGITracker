#!/usr/bin/env python3
"""
Load comprehensive signposts (v2) into database.

Loads all 89 signposts with rich metadata from signposts_comprehensive_v2.yaml
Idempotent - safe to run multiple times (upserts existing signposts)
"""

import sys
from pathlib import Path
import yaml
from datetime import datetime

# Add services/etl to path
sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "etl"))

from app.database import SessionLocal
from app.models import Signpost


def parse_date(date_str):
    """Parse date string to date object"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        return None


def load_signposts():
    """Load all signposts from comprehensive YAML"""
    
    yaml_path = Path(__file__).parent.parent / "infra" / "seeds" / "signposts_comprehensive_v2.yaml"
    
    print(f"📖 Loading from: {yaml_path}")
    
    with open(yaml_path) as f:
        data = yaml.safe_load(f)
    
    db = SessionLocal()
    stats = {"created": 0, "updated": 0, "skipped": 0}
    
    # Process each category
    categories = [
        'capabilities', 'agents', 'inputs', 'security',
        'economic', 'research', 'geopolitical', 'safety_incidents'
    ]
    
    for category_key in categories:
        if category_key not in data:
            continue
            
        signposts = data[category_key]
        print(f"\n📊 Processing {category_key}: {len(signposts)} signposts")
        
        for sp_data in signposts:
            code = sp_data['code']
            
            # Check if exists
            existing = db.query(Signpost).filter(Signpost.code == code).first()
            
            if existing:
                # Update existing
                for key, value in sp_data.items():
                    if key in ['aschenbrenner_timeline', 'ai2027_timeline', 'cotra_timeline', 
                               'epoch_timeline', 'openai_prep_timeline', 'current_sota_date']:
                        value = parse_date(value)
                    
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                
                print(f"  ✓ Updated: {code}")
                stats["updated"] += 1
            else:
                # Create new
                # Parse date fields
                for key in ['aschenbrenner_timeline', 'ai2027_timeline', 'cotra_timeline',
                            'epoch_timeline', 'openai_prep_timeline', 'current_sota_date']:
                    if key in sp_data:
                        sp_data[key] = parse_date(sp_data[key])
                
                new_signpost = Signpost(**sp_data)
                db.add(new_signpost)
                print(f"  ✓ Created: {code}")
                stats["created"] += 1
    
    db.commit()
    
    print(f"\n✅ Complete!")
    print(f"   Created: {stats['created']}")
    print(f"   Updated: {stats['updated']}")
    print(f"   Total signposts: {stats['created'] + stats['updated']}")
    
    # Verify count
    total = db.query(Signpost).count()
    print(f"\n📊 Database now has {total} signposts")
    
    # Count by category
    for cat in categories:
        count = db.query(Signpost).filter(Signpost.category == cat).count()
        if count > 0:
            print(f"   {cat}: {count}")
    
    db.close()


if __name__ == "__main__":
    load_signposts()

