"""
AGI Signpost Tracker - Streamlit Demo
Interactive dashboard showing real AI news mapped to AGI signposts.
"""
import streamlit as st
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime

# Add services/etl to path
sys.path.insert(0, str(Path(__file__).parent / "services" / "etl"))

from app.database import SessionLocal
from app.models import Event, EventSignpostLink, Signpost, RoadmapPrediction, Roadmap

st.set_page_config(
    page_title="AGI Signpost Tracker",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.tier-a { background-color: #dcfce7; padding: 4px 8px; border-radius: 4px; font-weight: bold; color: #166534; }
.tier-b { background-color: #dbeafe; padding: 4px 8px; border-radius: 4px; font-weight: bold; color: #1e40af; }
.tier-c { background-color: #fef3c7; padding: 4px 8px; border-radius: 4px; font-weight: bold; color: #92400e; }
.tier-d { background-color: #f3f4f6; padding: 4px 8px; border-radius: 4px; font-weight: bold; color: #374151; }
.if-true { background-color: #fef3c7; border-left: 4px solid #f59e0b; padding: 12px; margin: 8px 0; }
</style>
""", unsafe_allow_html=True)

# Title
st.title("🎯 AGI Signpost Tracker")
st.markdown("**Evidence-first dashboard tracking proximity to AGI via real AI news**")

# Sidebar
with st.sidebar:
    st.header("Filters")
    tier_filter = st.selectbox("Evidence Tier", ["All", "A", "B", "C", "D"])
    show_linked_only = st.checkbox("Show linked events only", value=False)
    
    st.markdown("---")
    st.markdown("### Evidence Tiers")
    st.markdown("🟢 **A**: Peer-reviewed (moves gauges)")
    st.markdown("🔵 **B**: Official labs (provisional)")
    st.markdown("🟡 **C**: Press (if true only)")
    st.markdown("⚪ **D**: Social (if true only)")

# Load data
@st.cache_data(ttl=60)
def load_events():
    db = SessionLocal()
    try:
        events = db.query(Event).order_by(Event.published_at.desc()).all()
        result = []
        for e in events:
            links = db.query(EventSignpostLink).filter(EventSignpostLink.event_id == e.id).all()
            signposts = []
            for link in links:
                sp = db.query(Signpost).filter(Signpost.id == link.signpost_id).first()
                if sp:
                    signposts.append({
                        "code": sp.code,
                        "name": sp.name,
                        "confidence": float(link.confidence) if link.confidence else 0,
                        "rationale": link.rationale
                    })
            result.append({
                "id": e.id,
                "title": e.title,
                "summary": e.summary,
                "tier": e.evidence_tier,
                "source_type": e.source_type,
                "publisher": e.publisher,
                "url": e.source_url,
                "published_at": e.published_at,
                "signposts": signposts,
                "provisional": e.provisional,
                "needs_review": e.needs_review
            })
        return result
    finally:
        db.close()

events = load_events()

# Apply filters
filtered = events
if tier_filter != "All":
    filtered = [e for e in filtered if e["tier"] == tier_filter]
if show_linked_only:
    filtered = [e for e in filtered if len(e["signposts"]) > 0]

# Stats
st.header("📊 Real-Time Stats")
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Events", len(events))
with col2:
    linked = sum(1 for e in events if len(e["signposts"]) > 0)
    st.metric("Auto-Mapped", f"{linked}/{len(events)}", f"{linked/len(events)*100:.0f}%")
with col3:
    total_links = sum(len(e["signposts"]) for e in events)
    st.metric("Total Links", total_links)
with col4:
    high_conf = sum(1 for e in events for sp in e["signposts"] if sp["confidence"] >= 0.7)
    st.metric("Links ≥0.7 conf", f"{high_conf}/{total_links}")

# Events list
st.header("📰 AI News & Research")
st.caption(f"Showing {len(filtered)} of {len(events)} events")

for event in filtered:
    tier_class = f"tier-{event['tier'].lower()}"
    tier_emoji = {"A": "🟢", "B": "🔵", "C": "🟡", "D": "⚪"}[event["tier"]]
    
    with st.expander(f"{tier_emoji} **{event['title']}**", expanded=False):
        # Tier badge
        st.markdown(f"<span class='{tier_class}'>Tier {event['tier']}</span> &nbsp; "
                   f"<small>{event['publisher']} • {event['published_at'].strftime('%b %d, %Y') if event['published_at'] else 'No date'}</small>", 
                   unsafe_allow_html=True)
        
        # If true banner for C/D
        if event["tier"] in ["C", "D"]:
            st.markdown(
                f"<div class='if-true'>⚠️ <strong>\"If True\" Analysis:</strong> "
                f"This {event['tier']}-tier {event['source_type']} does NOT move main gauges. "
                f"Tracked for research purposes only.</div>",
                unsafe_allow_html=True
            )
        
        # Summary
        if event["summary"]:
            st.write(event["summary"])
        
        # Signpost links
        if event["signposts"]:
            st.markdown("**Mapped to signposts:**")
            for sp in event["signposts"]:
                conf_color = "🟢" if sp["confidence"] >= 0.9 else "🟡" if sp["confidence"] >= 0.7 else "🔴"
                st.markdown(f"- {conf_color} **{sp['code']}**: {sp['name']} (confidence: {sp['confidence']:.2f})")
                if sp["rationale"]:
                    st.caption(f"  _{sp['rationale']}_")
        else:
            st.info("No signpost mappings found")
        
        # Source link
        if event["url"]:
            st.markdown(f"[📎 Source]({event['url']})")

# Footer
st.markdown("---")
st.caption("✅ All events are real AI news from 2023-2024 • No synthetic or hallucinated data • CC BY 4.0")
