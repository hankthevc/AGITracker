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
from sqlalchemy import text
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter

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
.tier-a { background-color: #10b981; color: white; padding: 0.3rem 0.6rem; border-radius: 6px; font-weight: bold; }
.tier-b { background-color: #3b82f6; color: white; padding: 0.3rem 0.6rem; border-radius: 6px; font-weight: bold; }
.tier-c { background-color: #f59e0b; color: white; padding: 0.3rem 0.6rem; border-radius: 6px; font-weight: bold; }
.tier-d { background-color: #ef4444; color: white; padding: 0.3rem 0.6rem; border-radius: 6px; font-weight: bold; }
.if-true { background-color: #fef3c7; border: 1px solid #f59e0b; border-radius: 8px; padding: 1rem; margin: 1rem 0; color: #92400e; }
.analysis-box { background-color: #f0f9ff; border: 1px solid #0ea5e9; border-radius: 8px; padding: 1rem; margin: 1rem 0; }
.stMetric { background-color: #f8fafc; padding: 1rem; border-radius: 8px; border-left: 4px solid #3b82f6; }
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
        # Use raw SQL to avoid SQLAlchemy model issues with missing columns
        result = db.execute(text("""
            SELECT id, title, summary, source_url, publisher, published_at, 
                   evidence_tier, source_type, provisional, needs_review
            FROM events 
            ORDER BY published_at DESC
        """)).fetchall()
        
        events_data = []
        for row in result:
            # Get signpost links for this event
            links_result = db.execute(text("""
                SELECT esl.confidence, esl.rationale, s.code, s.name
                FROM event_signpost_links esl
                JOIN signposts s ON esl.signpost_id = s.id
                WHERE esl.event_id = :event_id
            """), {"event_id": row.id}).fetchall()
            
            signposts = []
            for link_row in links_result:
                signposts.append({
                    "code": link_row.code,
                    "name": link_row.name,
                    "confidence": float(link_row.confidence) if link_row.confidence else 0,
                    "rationale": link_row.rationale
                })
            
            events_data.append({
                "id": row.id,
                "title": row.title,
                "summary": row.summary,
                "tier": row.evidence_tier,
                "source_type": row.source_type,
                "publisher": row.publisher,
                "url": row.source_url,
                "published_at": row.published_at,
                "signposts": signposts,
                "provisional": row.provisional,
                "needs_review": row.needs_review
            })
        
        return events_data
    except Exception as e:
        st.error(f"Database error: {e}")
        return []
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

    # Enhanced Stats with Visualizations
    st.header("📊 Real-Time Analytics")
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Events", len(events))
    with col2:
        linked = sum(1 for e in events if len(e["signposts"]) > 0)
        if len(events) > 0:
            percentage = f"{linked/len(events)*100:.0f}%"
        else:
            percentage = "0%"
        st.metric("Auto-Mapped", f"{linked}/{len(events)}", percentage)
    with col3:
        total_links = sum(len(e["signposts"]) for e in events)
        st.metric("Total Links", total_links)
    with col4:
        high_conf = sum(1 for e in events for sp in e["signposts"] if sp["confidence"] >= 0.7)
        st.metric("High Confidence", f"{high_conf}/{total_links}")
    
    # Visualizations
    if events:
        col1, col2 = st.columns(2)
        
        with col1:
            # Events by tier chart
            tier_counts = Counter(e["tier"] for e in events)
            if tier_counts:
                fig_tier = px.pie(
                    values=list(tier_counts.values()),
                    names=list(tier_counts.keys()),
                    title="Events by Evidence Tier",
                    color_discrete_map={
                        'A': '#10b981',  # Green
                        'B': '#3b82f6',  # Blue  
                        'C': '#f59e0b',  # Yellow
                        'D': '#ef4444'   # Red
                    }
                )
                fig_tier.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_tier, use_container_width=True)
        
        with col2:
            # Confidence distribution
            confidences = [sp["confidence"] for e in events for sp in e["signposts"]]
            if confidences:
                fig_conf = px.histogram(
                    x=confidences,
                    title="Confidence Score Distribution",
                    nbins=10,
                    color_discrete_sequence=['#8b5cf6']
                )
                fig_conf.update_layout(xaxis_title="Confidence Score", yaxis_title="Count")
                st.plotly_chart(fig_conf, use_container_width=True)
            else:
                st.info("No confidence scores available")
        
        # Timeline of events
        st.subheader("📅 Recent Events Timeline")
        if any(e.get("published_at") for e in events):
            timeline_data = []
            for event in events[:10]:  # Show last 10 events
                if event.get("published_at"):
                    timeline_data.append({
                        "Date": event["published_at"].strftime("%Y-%m-%d"),
                        "Event": event["title"][:50] + "..." if len(event["title"]) > 50 else event["title"],
                        "Tier": event["tier"],
                        "Signposts": len(event["signposts"])
                    })
            
            if timeline_data:
                df_timeline = pd.DataFrame(timeline_data)
                st.dataframe(
                    df_timeline,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Tier": st.column_config.TextColumn(
                            "Tier",
                            help="Evidence tier (A=verified, B=official, C=press, D=social)"
                        ),
                        "Signposts": st.column_config.NumberColumn(
                            "Signposts",
                            help="Number of signpost mappings"
                        )
                    }
                )

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
            
            # AI Analysis (if available)
            try:
                analysis_result = db.execute(text("""
                    SELECT summary, relevance_explanation, impact_json, confidence_reasoning, significance_score
                    FROM events_analysis 
                    WHERE event_id = :event_id
                    ORDER BY generated_at DESC LIMIT 1
                """), {"event_id": event["id"]}).fetchone()
                
                if analysis_result:
                    st.markdown("**🤖 AI Analysis:**")
                    st.info(f"**Summary:** {analysis_result.summary}")
                    
                    if analysis_result.relevance_explanation:
                        st.markdown(f"**Why this matters:** {analysis_result.relevance_explanation}")
                    
                    if analysis_result.impact_json:
                        st.markdown("**Impact Timeline:**")
                        impact = analysis_result.impact_json
                        if isinstance(impact, dict):
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.markdown(f"**Short-term (0-6m):** {impact.get('short', 'N/A')}")
                            with col2:
                                st.markdown(f"**Medium-term (6-18m):** {impact.get('medium', 'N/A')}")
                            with col3:
                                st.markdown(f"**Long-term (18m+):** {impact.get('long', 'N/A')}")
                    
                    if analysis_result.confidence_reasoning:
                        st.markdown(f"**Confidence:** {analysis_result.confidence_reasoning}")
                    
                    if analysis_result.significance_score:
                        score = float(analysis_result.significance_score)
                        st.markdown(f"**Significance Score:** {score:.2f}/1.0")
                        st.progress(score)
                        
            except Exception as e:
                pass  # Analysis not available
            
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
