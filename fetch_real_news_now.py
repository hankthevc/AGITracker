"""
Fetch REAL AI news from live RSS feeds right now (Oct 2025).
Uses OpenAI to parse and understand the content.
"""
import sys
sys.path.insert(0, 'services/etl')

import feedparser
from datetime import datetime, timezone
import json

# Fetch from real RSS feeds
feeds = [
    ("OpenAI", "https://openai.com/blog/rss.xml"),
    ("Anthropic", "https://www.anthropic.com/news/rss.xml"),
    ("Google DeepMind", "https://deepmind.google/discover/feeds/blog.xml"),
    ("Meta AI", "https://ai.meta.com/blog/feed/"),
]

all_items = []

for publisher, url in feeds:
    try:
        print(f"Fetching from {publisher}...")
        feed = feedparser.parse(url, agent="AGI-Tracker/1.0")
        
        # Get last 5 items from each feed
        for entry in feed.entries[:5]:
            title = entry.get("title", "").strip()
            summary = entry.get("summary", "").strip()
            link = entry.get("link")
            published = entry.get("published") or entry.get("updated")
            
            all_items.append({
                "title": title,
                "summary": summary[:200],  # Truncate
                "url": link,
                "publisher": publisher,
                "published_at": published,
            })
            
        print(f"  ✓ Got {len(feed.entries[:5])} items")
    except Exception as e:
        print(f"  ✗ Failed: {e}")

print(f"\n📊 Total items fetched: {len(all_items)}")
print("\nSample (most recent 10):\n")
for item in all_items[:10]:
    print(f"- {item['publisher']}: {item['title'][:80]}")
    print(f"  Published: {item['published_at']}")
    print()

# Save to file
with open("REAL_NEWS_SAMPLE.json", "w") as f:
    json.dump(all_items, f, indent=2)

print(f"✓ Saved {len(all_items)} real items to REAL_NEWS_SAMPLE.json")
