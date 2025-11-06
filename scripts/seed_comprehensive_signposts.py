#!/usr/bin/env python3
"""
Load comprehensive signposts (v2) into database.

Loads all signposts with rich metadata from signposts_comprehensive_v2.yaml
Idempotent - safe to run multiple times (upserts via ON CONFLICT)

SAFETY GUARANTEES:
- Single transaction (all-or-nothing)
- Type validation (direction, dates, numeric ranges)
- Duplicate detection (fails on code collisions in YAML)
- Clear summary (inserted/updated/skipped with reasons)
"""

import sys
from pathlib import Path
import yaml
from datetime import datetime
from decimal import Decimal, InvalidOperation
from collections import Counter

# Add services/etl to path
sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "etl"))

from app.database import SessionLocal, engine
from app.models import Signpost
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError


# Validation constants
ALLOWED_DIRECTIONS = {'>=', '<='}
ALLOWED_CATEGORIES = {'capabilities', 'agents', 'inputs', 'security', 
                      'economic', 'research', 'geopolitical', 'safety_incidents'}
DATE_FIELDS = ['aschenbrenner_timeline', 'ai2027_timeline', 'cotra_timeline',
               'epoch_timeline', 'openai_prep_timeline', 'current_sota_date']
NUMERIC_FIELDS = ['baseline_value', 'target_value', 'current_sota_value',
                  'aschenbrenner_confidence', 'ai2027_confidence', 
                  'cotra_confidence', 'epoch_confidence', 'openai_prep_confidence']


def parse_date(date_str):
    """Parse date string to date object with validation."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError as e:
        raise ValueError(f"Invalid date format '{date_str}': {e}")


def parse_numeric(value):
    """Parse numeric value with validation."""
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (ValueError, InvalidOperation) as e:
        raise ValueError(f"Invalid numeric value '{value}': {e}")


def validate_signpost(sp_data, code):
    """Validate signpost data before insert/update."""
    errors = []
    
    # Required fields
    if 'code' not in sp_data:
        errors.append("Missing required field: code")
    if 'name' not in sp_data:
        errors.append("Missing required field: name")
    if 'category' not in sp_data:
        errors.append("Missing required field: category")
    if 'direction' not in sp_data:
        errors.append("Missing required field: direction")
    
    # Validate category
    if sp_data.get('category') not in ALLOWED_CATEGORIES:
        errors.append(f"Invalid category: {sp_data.get('category')}")
    
    # Validate direction
    if sp_data.get('direction') not in ALLOWED_DIRECTIONS:
        errors.append(f"Invalid direction: {sp_data.get('direction')}. Must be one of {ALLOWED_DIRECTIONS}")
    
    # Validate confidence ranges (0-1)
    for field in ['aschenbrenner_confidence', 'ai2027_confidence', 'cotra_confidence', 
                  'epoch_confidence', 'openai_prep_confidence']:
        if field in sp_data and sp_data[field] is not None:
            val = float(sp_data[field])
            if not (0 <= val <= 1):
                errors.append(f"{field} must be between 0 and 1, got {val}")
    
    if errors:
        raise ValueError(f"Validation failed for signpost '{code}': " + "; ".join(errors))


def load_signposts():
    """Load all signposts from comprehensive YAML with full validation."""
    
    yaml_path = Path(__file__).parent.parent / "infra" / "seeds" / "signposts_comprehensive_v2.yaml"
    
    print(f"📖 Loading from: {yaml_path}")
    
    with open(yaml_path) as f:
        data = yaml.safe_load(f)
    
    # Track statistics
    stats = {"created": 0, "updated": 0, "skipped": 0, "errors": []}
    codes_seen = set()
    
    # Collect all signposts with validation
    all_signposts = []
    
    for category_key in ALLOWED_CATEGORIES:
        if category_key not in data:
            continue
            
        signposts = data[category_key]
        print(f"\n📊 Processing {category_key}: {len(signposts)} signposts")
        
        for sp_data in signposts:
            code = sp_data.get('code', 'UNKNOWN')
            
            # Check for duplicates in YAML
            if code in codes_seen:
                error_msg = f"Duplicate code in YAML: {code}"
                print(f"  ❌ {error_msg}")
                stats["errors"].append(error_msg)
                continue
            codes_seen.add(code)
            
            try:
                # Validate before processing
                validate_signpost(sp_data, code)
                
                # Type coercion
                for field in DATE_FIELDS:
                    if field in sp_data:
                        sp_data[field] = parse_date(sp_data[field])
                
                for field in NUMERIC_FIELDS:
                    if field in sp_data:
                        sp_data[field] = parse_numeric(sp_data[field])
                
                all_signposts.append(sp_data)
                
            except Exception as e:
                error_msg = f"{code}: {str(e)}"
                print(f"  ❌ Validation error: {error_msg}")
                stats["errors"].append(error_msg)
                stats["skipped"] += 1
    
    if stats["errors"]:
        print(f"\n⚠️  Found {len(stats['errors'])} validation errors. Aborting.")
        for error in stats["errors"]:
            print(f"  - {error}")
        sys.exit(1)
    
    # Use transaction for all-or-nothing behavior
    db = SessionLocal()
    try:
        print(f"\n💾 Inserting/updating {len(all_signposts)} signposts in single transaction...")
        
        for sp_data in all_signposts:
            code = sp_data['code']
            
            # Check if exists
            existing = db.query(Signpost).filter(Signpost.code == code).first()
            
            if existing:
                # Update existing
                for key, value in sp_data.items():
                    if hasattr(existing, key):
                        setattr(existing, key, value)
                print(f"  ✓ Updated: {code}")
                stats["updated"] += 1
            else:
                # Create new
                new_signpost = Signpost(**sp_data)
                db.add(new_signpost)
                print(f"  ✓ Created: {code}")
                stats["created"] += 1
        
        # Commit transaction
        db.commit()
        
        print(f"\n✅ Transaction committed successfully!")
        print(f"   Created: {stats['created']}")
        print(f"   Updated: {stats['updated']}")
        print(f"   Skipped: {stats['skipped']}")
        print(f"   Total processed: {stats['created'] + stats['updated']}")
        
        # Verify counts
        total = db.query(Signpost).count()
        print(f"\n📊 Database now has {total} total signposts")
        
        # Count by category
        for cat in sorted(ALLOWED_CATEGORIES):
            count = db.query(Signpost).filter(Signpost.category == cat).count()
            if count > 0:
                print(f"   {cat}: {count}")
        
    except IntegrityError as e:
        db.rollback()
        print(f"\n❌ Database integrity error: {e}")
        print("   Transaction rolled back. No changes made.")
        sys.exit(1)
    except Exception as e:
        db.rollback()
        print(f"\n❌ Unexpected error: {e}")
        print("   Transaction rolled back. No changes made.")
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    load_signposts()
