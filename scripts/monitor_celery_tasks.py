#!/usr/bin/env python3
"""
Monitor Celery tasks and Beat schedule.

Usage:
    python scripts/monitor_celery_tasks.py --mode [active|scheduled|stats|all]
"""
import argparse
import sys
from datetime import datetime
from pathlib import Path

# Add services/etl to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "services" / "etl"))

from celery import Celery
from app.config import settings


def get_celery_app():
    """Initialize Celery app for inspection."""
    celery_app = Celery(
        "agi_tracker_etl",
        broker=settings.redis_url,
        backend=settings.redis_url,
    )
    return celery_app


def show_active_tasks(celery_app):
    """Show currently running tasks."""
    print("\n" + "="*60)
    print("📋 ACTIVE TASKS")
    print("="*60)
    
    inspect = celery_app.control.inspect()
    active = inspect.active()
    
    if not active:
        print("⚠️  No workers available or no active tasks")
        return
    
    total_active = 0
    for worker, tasks in active.items():
        if tasks:
            print(f"\n🔧 Worker: {worker}")
            for task in tasks:
                print(f"  - {task['name']}")
                print(f"    ID: {task['id'][:16]}...")
                print(f"    Started: {task.get('time_start', 'N/A')}")
            total_active += len(tasks)
        else:
            print(f"\n🔧 Worker: {worker} - idle")
    
    print(f"\nTotal active tasks: {total_active}")


def show_scheduled_tasks(celery_app):
    """Show scheduled (upcoming) tasks."""
    print("\n" + "="*60)
    print("⏰ SCHEDULED TASKS")
    print("="*60)
    
    inspect = celery_app.control.inspect()
    scheduled = inspect.scheduled()
    
    if not scheduled:
        print("⚠️  No workers available or no scheduled tasks")
        return
    
    total_scheduled = 0
    for worker, tasks in scheduled.items():
        if tasks:
            print(f"\n🔧 Worker: {worker}")
            for task in tasks:
                eta = task.get('eta', 'N/A')
                print(f"  - {task['request']['name']}")
                print(f"    ETA: {eta}")
                print(f"    ID: {task['request']['id'][:16]}...")
            total_scheduled += len(tasks)
        else:
            print(f"\n🔧 Worker: {worker} - no scheduled tasks")
    
    print(f"\nTotal scheduled tasks: {total_scheduled}")


def show_beat_schedule(celery_app):
    """Show Beat schedule configuration."""
    print("\n" + "="*60)
    print("📅 BEAT SCHEDULE CONFIGURATION")
    print("="*60)
    
    from app.celery_app import celery_app as configured_app
    
    schedule = configured_app.conf.beat_schedule
    
    if not schedule:
        print("⚠️  No beat schedule configured")
        return
    
    # Group by category
    categories = {
        "News Ingestion": [],
        "Benchmark Fetching": [],
        "Event Processing": [],
        "Daily/Weekly Tasks": [],
    }
    
    for task_name, config in schedule.items():
        task = config['task']
        cron = config['schedule']
        
        if 'ingest' in task_name:
            categories["News Ingestion"].append((task_name, task, cron))
        elif 'fetch' in task_name or 'osworld' in task_name or 'webarena' in task_name:
            categories["Benchmark Fetching"].append((task_name, task, cron))
        elif 'map' in task_name or 'analysis' in task_name:
            categories["Event Processing"].append((task_name, task, cron))
        else:
            categories["Daily/Weekly Tasks"].append((task_name, task, cron))
    
    for category, tasks in categories.items():
        if tasks:
            print(f"\n📂 {category} ({len(tasks)} tasks)")
            print("-" * 60)
            for task_name, task, cron in sorted(tasks):
                # Format cron schedule (handle both int and set types)
                hour = list(cron.hour)[0] if isinstance(cron.hour, set) else cron.hour
                minute = list(cron.minute)[0] if isinstance(cron.minute, set) else cron.minute
                cron_str = f"{hour:02d}:{minute:02d} UTC"
                
                if hasattr(cron, 'day_of_week') and cron.day_of_week is not None:
                    days = {0: 'Sun', 1: 'Mon', 2: 'Tue', 3: 'Wed', 4: 'Thu', 5: 'Fri', 6: 'Sat'}
                    dow = list(cron.day_of_week)[0] if isinstance(cron.day_of_week, set) else cron.day_of_week
                    cron_str += f" ({days.get(dow, dow)})"
                else:
                    cron_str += " (daily)"
                
                print(f"  {task_name}")
                print(f"    Task: {task}")
                print(f"    Schedule: {cron_str}")


def show_worker_stats(celery_app):
    """Show worker statistics."""
    print("\n" + "="*60)
    print("📊 WORKER STATISTICS")
    print("="*60)
    
    inspect = celery_app.control.inspect()
    
    # Worker stats
    stats = inspect.stats()
    if stats:
        for worker, stat_data in stats.items():
            print(f"\n🔧 Worker: {worker}")
            print(f"  Pool: {stat_data.get('pool', {}).get('implementation', 'N/A')}")
            print(f"  Max concurrency: {stat_data.get('pool', {}).get('max-concurrency', 'N/A')}")
            print(f"  Total tasks: {stat_data.get('total', {})}")
    else:
        print("⚠️  No workers available")
    
    # Registered tasks
    registered = inspect.registered()
    if registered:
        print("\n📋 Registered Tasks:")
        for worker, tasks in registered.items():
            print(f"\n  Worker: {worker}")
            # Filter to our tasks only
            our_tasks = [t for t in tasks if 'app.tasks' in t or 'ingest' in t or 'fetch' in t]
            for task in sorted(our_tasks):
                print(f"    - {task}")
    
    # Reserved tasks
    reserved = inspect.reserved()
    if reserved:
        total_reserved = sum(len(tasks) for tasks in reserved.values())
        print(f"\n⏳ Reserved (waiting) tasks: {total_reserved}")


def main():
    parser = argparse.ArgumentParser(description="Monitor Celery tasks and schedule")
    parser.add_argument(
        "--mode",
        choices=["active", "scheduled", "schedule", "stats", "all"],
        default="all",
        help="What to display"
    )
    args = parser.parse_args()
    
    print("="*60)
    print("🔍 CELERY MONITOR")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC")
    print("="*60)
    
    celery_app = get_celery_app()
    
    if args.mode in ["active", "all"]:
        show_active_tasks(celery_app)
    
    if args.mode in ["scheduled", "all"]:
        show_scheduled_tasks(celery_app)
    
    if args.mode in ["schedule", "all"]:
        show_beat_schedule(celery_app)
    
    if args.mode in ["stats", "all"]:
        show_worker_stats(celery_app)
    
    print("\n" + "="*60)
    print("✅ Monitor complete")
    print("="*60)
    
    # Notes for production
    print("\n📝 Production Commands:")
    print("  Railway logs: railway logs --service celery-worker")
    print("  Railway logs: railway logs --service celery-beat")
    print("  Inspect tasks: railway run celery -A app.celery_app inspect active")
    print("  Inspect schedule: railway run celery -A app.celery_app inspect scheduled")


if __name__ == "__main__":
    main()

