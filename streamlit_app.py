"""
AGI Signpost Tracker - Streamlit Demo
Interactive dashboard showing real AI news mapped to AGI signposts.
"""
import streamlit as st
import sys
import os
from pathlib import Path
import pandas as pd
from datetime import datetime

# Check for DATABASE_URL
db_url = os.environ.get("DATABASE_URL") or st.secrets.get("DATABASE_URL")
if not db_url:
    st.error("❌ DATABASE_URL not configured. Set in environment or Streamlit secrets.")
    st.stop()

# Ensure DATABASE_URL uses psycopg driver (not psycopg2)
if db_url.startswith("postgresql://"):
    db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
os.environ["DATABASE_URL"] = db_url

# Add services/etl to path
sys.path.insert(0, str(Path(__file__).parent / "services" / "etl"))

try:
    from app.database import SessionLocal
    from app.models import Event, EventSignpostLink, Signpost, SignpostContent
except ImportError as e:
    st.error(f"❌ Failed to import database models: {e}")
    st.info("Make sure all dependencies are installed: `pip install -r requirements.txt`")
    st.info(f"Database URL: {db_url[:50]}...")
    st.stop()

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
    page = st.radio("Navigate", ["📰 News Feed", "🎯 Signposts"], index=0)
    
    st.markdown("---")
    
    # Initialize filter variables
    tier_filter = "All"
    show_linked_only = False
    
    if page == "📰 News Feed":
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

if page == "📰 News Feed":
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

if page == "🎯 Signposts":
    # Signposts page
    st.header("🎯 AGI Signposts with Citations")
    
    @st.cache_data(ttl=300)
    def load_signposts_with_content():
        db = SessionLocal()
        try:
            signposts = db.query(Signpost).filter(Signpost.first_class == True).all()
            result = []
            for sp in signposts:
                content = db.query(SignpostContent).filter(SignpostContent.signpost_id == sp.id).first()
                result.append({
                    "code": sp.code,
                    "name": sp.name,
                    "category": sp.category,
                    "first_class": sp.first_class,
                    "why_matters": content.why_matters if content else None,
                    "current_state": content.current_state if content else None,
                    "key_papers": content.key_papers if content else [],
                    "technical": content.technical_explanation if content else None,
                })
            return result
        finally:
            db.close()
    
    signposts = load_signposts_with_content()
    
    # Group by category
    categories = {"capabilities": [], "agents": [], "inputs": [], "security": []}
    for sp in signposts:
        if sp["category"] in categories:
            categories[sp["category"]].append(sp)
    
    for cat_name, cat_signposts in categories.items():
        if not cat_signposts:
            continue
        st.subheader(f"📊 {cat_name.title()}")
        
        for sp in cat_signposts:
            with st.expander(f"**{sp['name']}** ({sp['code']})", expanded=False):
                if sp["why_matters"]:
                    st.markdown("**Why This Matters:**")
                    st.write(sp["why_matters"])
                
                if sp["current_state"]:
                    st.markdown("**Current State:**")
                    st.text(sp["current_state"])
                
                if sp["key_papers"]:
                    st.markdown("**Key Papers:**")
                    for paper in sp["key_papers"]:
                        st.markdown(f"- [{paper.get('title', 'Paper')}]({paper.get('url', '#')}) - {paper.get('citation', '')}")
                        if paper.get("summary"):
                            st.caption(paper["summary"])
                
                if sp["technical"]:
                    st.markdown("**Technical Details:**")
                    st.text(sp["technical"])

# Footer
st.markdown("---")
st.caption("✅ All events are real AI news from 2023-2024 • No synthetic or hallucinated data • CC BY 4.0")
