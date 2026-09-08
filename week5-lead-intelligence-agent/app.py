"""
Nexariza AI — Week 5
Premium Editorial B2B SaaS Intelligence Platform
"""

import os
import glob
import json
from datetime import datetime
import streamlit as st
from lead_agent import run_lead_pipeline

st.set_page_config(page_title="Nexariza AI | Lead Intelligence", page_icon="📈", layout="wide")

# ============================================================
# STATE MANAGEMENT
# ============================================================
if "page" not in st.session_state:
    st.session_state.page = "landing"
if "active_batch" not in st.session_state:
    st.session_state.active_batch = None
if "selected_lead_idx" not in st.session_state:
    st.session_state.selected_lead_idx = None

# ============================================================
# GLOBAL CSS — IVORY, SAGE, TERRA COTTA
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* Structure & Background */
html, body, [class*="css"] { font-family: 'Manrope', sans-serif; }
.stApp { background-color: #F4F0E8; color: #2F3A34; background-image: radial-gradient(#8FA58D 0.5px, transparent 0.5px); background-size: 20px 20px; opacity: 0.98; }
section[data-testid="stSidebar"] { display: none !important; }

/* Top Nav */
.top-nav { position: fixed; top: 0; left: 0; right: 0; z-index: 999; background: rgba(244, 240, 232, 0.9); backdrop-filter: blur(10px); border-bottom: 1px solid #D8D0C2; padding: 15px 40px; display: flex; justify-content: space-between; align-items: center; }
.top-nav-logo { font-weight: 800; font-size: 18px; color: #2F3A34; letter-spacing: 1px; }
.top-nav-links { font-size: 14px; font-weight: 600; color: #C96F52; display: flex; gap: 30px; }

/* ============================================================
   LANDING PAGE STYLES
   ============================================================ */
.hero { padding: 140px 0 80px 0; text-align: center; position: relative; overflow: hidden; }
.hero-eyebrow { font-family: 'JetBrains Mono', monospace; font-size: 12px; letter-spacing: 4px; color: #C96F52; margin-bottom: 20px; }
.hero-title { font-size: 72px; font-weight: 800; color: #2F3A34; line-height: 1.05; margin-bottom: 20px; }
.hero-title span { color: #C96F52; }
.hero-sub { font-size: 20px; color: #5C6B62; max-width: 700px; margin: 0 auto 40px auto; }
.hero-author { font-family: 'JetBrains Mono', monospace; font-size: 16px; color: #8FA58D; margin-bottom: 50px; }

/* Feature Grid */
.features-wrap { max-width: 1200px; margin: 0 auto; padding: 50px 20px; }
.feature-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; }
.feature-card { background: #FBF9F5; border: 1px solid #E3DCD2; border-radius: 16px; padding: 30px; text-align: left; box-shadow: 0 4px 20px rgba(47,58,52,0.03); }
.feature-title { font-size: 16px; font-weight: 800; color: #C96F52; margin-bottom: 10px; }
.feature-desc { font-size: 14px; color: #5C6B62; line-height: 1.6; }

/* ============================================================
   PROSPECTING PAGE
   ============================================================ */
.prospecting-wrap { max-width: 800px; margin: 0 auto; padding: 40px 20px; }
.prospecting-header { font-size: 32px; font-weight: 800; color: #2F3A34; margin-bottom: 10px; }
.prospecting-sub { font-size: 16px; color: #5C6B62; margin-bottom: 40px; }

/* Large, Readable Input */
div[data-testid="stTextInput"] > div {
    background: #2F3A34 !important; 
    border: 2px solid #8FA58D !important; 
    border-radius: 50px !important; 
    padding: 18px 24px !important; 
    box-shadow: 0 10px 30px rgba(47,58,52,0.1) !important;
}
div[data-testid="stTextInput"] input {
    color: #FFFFFF !important; 
    font-size: 20px !important; 
    font-weight: 500 !important;
    -webkit-text-fill-color: #FFFFFF !important;
}
div[data-testid="stTextInput"] input::placeholder { color: #8FA58D !important; font-size: 18px !important; }

/* Button styling */
.stFormSubmitButton button {
    background: #C96F52 !important; color: #F4F0E8 !important;
    font-weight: 700 !important; border: none !important; border-radius: 50px !important; 
    font-size: 18px !important; padding: 16px 30px !important; width: 100% !important;
    transition: all 0.3s ease !important;
}
.stFormSubmitButton button:hover { background: #B05A41 !important; transform: translateY(-2px); }

/* ============================================================
   DOSSIER & BOARD STYLES
   ============================================================ */
.board-container { max-width: 1400px; margin: 0 auto; padding: 40px; }
.board-header { font-size: 36px; font-weight: 800; color: #2F3A34; margin-bottom: 20px; }

/* Column Headers */
.nx-col-header { font-weight: 800; font-size: 14px; letter-spacing: 2px; padding: 15px; border-radius: 50px; margin-bottom: 20px; text-align: center; }
.header-hot { background: #F4F0E8; color: #C96F52; border: 2px solid #C96F52; }
.header-warm { background: #F4F0E8; color: #8FA58D; border: 2px solid #8FA58D; }
.header-cold { background: #E3DCD2; color: #5C6B62; border: 2px solid #5C6B62; }

/* Lead Cards */
.nx-card { background: #FBF9F5; border: 1px solid #E3DCD2; border-radius: 12px; padding: 20px; margin-bottom: 15px; }
.nx-card:hover { border-color: #C96F52; box-shadow: 0 8px 25px rgba(201,111,82,0.1); }
.nx-company { font-size: 18px; font-weight: 800; color: #2F3A34; }

/* Dossier */
.dossier-header { font-size: 42px; font-weight: 800; color: #2F3A34; margin-bottom: 5px; }
.dossier-badge { display: inline-block; font-weight: 700; padding: 5px 15px; border-radius: 50px; margin-bottom: 30px; }
.badge-hot { background: #C96F52; color: #F4F0E8; }
.badge-warm { background: #8FA58D; color: #F4F0E8; }
.badge-cold { background: #5C6B62; color: #F4F0E8; }

.dossier-section { background: #FBF9F5; border: 1px solid #E3DCD2; border-radius: 16px; padding: 30px; margin-bottom: 20px; }
.section-title { font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 700; letter-spacing: 2px; color: #C96F52; margin-bottom: 15px; }

.outreach-box { background: #F4F0E8; border: 1px solid #8FA58D; border-radius: 12px; padding: 25px; font-size: 15px; line-height: 1.8; white-space: pre-wrap; color: #2F3A34; margin-bottom: 20px; }
/* ============================================================
   FIX: Make Metric Text Dark & Visible
   ============================================================ */
div[data-testid="stMetricValue"] {
    color: #2F3A34 !important;
    font-family: 'Manrope', sans-serif !important;
    font-weight: 800 !important;
}
div[data-testid="stMetricLabel"] {
    color: #5C6B62 !important;
}
/* Native Streamlit Button Overrides for Dossier */
.stButton button {
    background: transparent !important; color: #2F3A34 !important;
    border: 2px solid #8FA58D !important; border-radius: 50px !important; 
    font-weight: 700 !important; font-size: 14px !important;
}
.stButton button:hover { background: #8FA58D !important; color: #F4F0E8 !important; }
/* Custom Metric Styling */
.nx-stat-card {
    background: #FBF9F5;
    border: 1px solid #E3DCD2;
    border-radius: 12px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 4px 10px rgba(47, 58, 52, 0.05);
    margin-bottom: 20px;
}
.nx-stat-number {
    font-size: 36px;
    font-weight: 800;
    color: #2F3A34; /* Dark green */
    line-height: 1.2;
}
.nx-stat-label {
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 2px;
    color: #5C6B62; /* Darker grey-green, fully visible */
    text-transform: uppercase;
    margin-top: 5px;
}
/* Fix Download Button */
.stDownloadButton button {
    background: transparent !important; 
    color: #2F3A34 !important;
    border: 2px solid #8FA58D !important; 
    border-radius: 50px !important; 
    font-weight: 700 !important; 
    font-size: 14px !important;
}
.stDownloadButton button:hover { 
    background: #8FA58D !important; 
    color: #F4F0E8 !important; 
}

/* Flowing Contour & Topographic Background Texture for Prospecting & Dossier */
.stApp {
    background-color: #F4F0E8;
    background-image: 
        /* Flowing low-opacity Sage contour lines */
        radial-gradient(ellipse at 20% 50%, rgba(143, 165, 141, 0.08) 0%, transparent 50%),
        radial-gradient(ellipse at 80% 20%, rgba(143, 165, 141, 0.06) 0%, transparent 50%),
        /* Muted Terracotta subtle wave */
        radial-gradient(ellipse at 50% 80%, rgba(201, 111, 82, 0.05) 0%, transparent 50%),
        /* Base color */
        #F4F0E8; 
}
</style>
""", unsafe_allow_html=True)

# ============================================================
# NAVIGATION
# ============================================================
def top_nav():
    st.markdown("""
    <div class="top-nav">
        <div class="top-nav-logo">NEXTARIZA AI</div>
        <div class="top-nav-links">Prospecting &nbsp;·&nbsp; Intelligence &nbsp;·&nbsp; Leads</div>
    </div>
    <div style="height: 70px;"></div>
    """, unsafe_allow_html=True)

# ============================================================
# PAGE 1: LANDING
# ============================================================
def render_landing():
    st.markdown("""
    <div class="hero">
        <div class="hero-eyebrow">ENTERPRISE SALES INTELLIGENCE</div>
        <div class="hero-title">Turn <span>Public Web Intelligence</span><br>into Qualified Prospects.</div>
        <div class="hero-sub">Turn public web intelligence into qualified prospects, prioritized opportunities, and personalized outreach.</div>
        <div class="hero-author">Built & Designed by Areeba Zaka</div>
    </div>
    
    <div class="features-wrap">
        <div class="feature-grid">
            <div class="feature-card">
                <div class="feature-title">DISCOVER</div>
                <div class="feature-desc">Find companies matching a target industry and market.</div>
            </div>
            <div class="feature-card">
                <div class="feature-title">ANALYZE</div>
                <div class="feature-desc">Analyze public company information and identify potential business needs.</div>
            </div>
            <div class="feature-card">
                <div class="feature-title">QUALIFY</div>
                <div class="feature-desc">Automatically score prospects and classify them as Hot, Warm, or Cold.</div>
            </div>
            <div class="feature-card">
                <div class="feature-title">ENGAGE</div>
                <div class="feature-desc">Generate highly personalized outreach based on company-specific intelligence.</div>
            </div>
        </div>
        <br><br>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("Start Prospecting →", use_container_width=True):
            st.session_state.page = "prospecting"
            st.rerun()

# ============================================================
# PAGE 2: PROSPECTING (CLEAN, LARGE INPUT)
# ============================================================
def render_prospecting():
    top_nav()
    
    # Custom HTML just for this section
    st.markdown("""
    <div style="max-width: 800px; margin: 60px auto 0 auto; padding: 0 20px; text-align: center;">
        <h1 style="font-size: 42px; font-weight: 800; color: #2F3A34; margin-bottom: 10px;">Find Your Next Opportunity</h1>
        <p style="font-size: 18px; color: #5C6B62; margin-bottom: 40px;">Enter a domain. Nextariza AI will discover relevant companies, analyze public signals, and identify potential AI needs.</p>
    </div>
    """, unsafe_allow_html=True)

    # The form
    with st.form(key="search_form"):
        # Large single box
        industry = st.text_input("Domain", placeholder="e.g. Healthcare AI, E-commerce, FinTech, AI SaaS", label_visibility="collapsed")
        
        # Button
        cta = st.form_submit_button("ANALYZE MARKET →")

        if cta:
            if not industry.strip():
                  st.warning("Please enter a domain!")
            else:
                   with st.spinner("Analyzing market and scoring leads... Please wait, this can take a minute."):
                    try:
                        # Reduced to 5 to avoid rate limits
                        leads = run_lead_pipeline(industry.strip(), target_count=5)
                        
                        # FORCE the name to be Areeba Zaka (removes [Your Name] placeholders)
                        for lead in leads:
                            msg = lead.get("outreach_message", "")
                            # Remove generic placeholders
                            msg = msg.replace("[Your Name]", "Areeba Zaka")
                            msg = msg.replace("[Your Title]", "Lead Qualification Assistant")
                            msg = msg.replace("[Company Name]", "Nexariza AI")
                            # Replace with the correct sign-off
                            lead["outreach_message"] = msg
                            
                        st.session_state.active_batch = {"industry": industry.strip(), "leads": leads}
                        st.session_state.page = "board"
                        st.rerun()
                    except Exception as e:
                        if "429" in str(e):
                            st.error("Rate limit reached! Please wait 60 seconds and try again.")
                        else:
                            st.error(f"Error: {e}")
                    except Exception as e:
                        if "429" in str(e):
                            st.error("Rate limit reached! Please wait 60 seconds and try again.")
                        else:
                            st.error(f"Error: {e}")

# ============================================================
# PAGE 3: INTELLIGENCE BOARD
# ============================================================
def render_board():
    top_nav()
    active = st.session_state.active_batch
    
    if not active:
        st.session_state.page = "prospecting"
        st.rerun()

    # Back to Search Button (No VS Code refresh needed!)
    if st.button("← Back to Search"):
        st.session_state.page = "prospecting"
        st.rerun()
        
    leads = active.get("leads", [])
    hot = [l for l in leads if l.get("score") == "Hot"]
    warm = [l for l in leads if l.get("score") == "Warm"]
    cold = [l for l in leads if l.get("score") == "Cold"]

    st.markdown(f'<div class="board-header">Lead Intelligence — {active["industry"]}</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f"""
        <div class="nx-stat-card">
            <div class="nx-stat-number">{len(leads)}</div>
            <div class="nx-stat-label">Total Leads</div>
        </div>
        """, unsafe_allow_html=True)
    
    with c2:
        st.markdown(f"""
        <div class="nx-stat-card">
            <div class="nx-stat-number" style="color: #C96F52;">{len(hot)}</div>
            <div class="nx-stat-label">Hot</div>
        </div>
        """, unsafe_allow_html=True)
    
    with c3:
        st.markdown(f"""
        <div class="nx-stat-card">
            <div class="nx-stat-number" style="color: #8FA58D;">{len(warm)}</div>
            <div class="nx-stat-label">Warm</div>
        </div>
        """, unsafe_allow_html=True)
    
    with c4:
        st.markdown(f"""
        <div class="nx-stat-card">
            <div class="nx-stat-number" style="color: #5C6B62;">{len(cold)}</div>
            <div class="nx-stat-label">Cold</div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("---")

    board_cols = st.columns(3)

    # Hot
    with board_cols[0]:
        st.markdown(f'<div class="nx-col-header header-hot">🔥 HOT LEADS ({len(hot)})</div>', unsafe_allow_html=True)
        for idx, lead in enumerate(leads):
            if lead in hot:
                with st.container(border=True):
                    st.markdown(f'<div class="nx-company">{lead.get("company", "Unknown")}</div>', unsafe_allow_html=True)
                    st.caption(lead.get("signal", "")[:60] + "...")
                    if st.button("View Intelligence →", key=f"hot_{idx}"):
                        st.session_state.selected_lead_idx = idx
                        st.session_state.page = "dossier"
                        st.rerun()

    # Warm
    with board_cols[1]:
        st.markdown(f'<div class="nx-col-header header-warm">🌿 WARM LEADS ({len(warm)})</div>', unsafe_allow_html=True)
        for idx, lead in enumerate(leads):
            if lead in warm:
                with st.container(border=True):
                    st.markdown(f'<div class="nx-company">{lead.get("company", "Unknown")}</div>', unsafe_allow_html=True)
                    st.caption(lead.get("signal", "")[:60] + "...")
                    if st.button("View Intelligence →", key=f"warm_{idx}"):
                        st.session_state.selected_lead_idx = idx
                        st.session_state.page = "dossier"
                        st.rerun()

    # Cold
    with board_cols[2]:
        st.markdown(f'<div class="nx-col-header header-cold">❄️ COLD LEADS ({len(cold)})</div>', unsafe_allow_html=True)
        for idx, lead in enumerate(leads):
            if lead in cold:
                with st.container(border=True):
                    st.markdown(f'<div class="nx-company">{lead.get("company", "Unknown")}</div>', unsafe_allow_html=True)
                    st.caption(lead.get("signal", "")[:60] + "...")
                    if st.button("View Intelligence →", key=f"cold_{idx}"):
                        st.session_state.selected_lead_idx = idx
                        st.session_state.page = "dossier"
                        st.rerun()

# ============================================================
# PAGE 4: DOSSIER & OUTREACH
# ============================================================
def render_dossier():
    top_nav()
    active = st.session_state.active_batch
    idx = st.session_state.selected_lead_idx

    if active and idx is not None:
        lead = active.get("leads", [])[idx]
        
        if st.button("← Back to Board"):
            st.session_state.page = "board"
            st.rerun()

        st.markdown(f'<div class="dossier-header">{lead.get("company", "Unknown")}</div>', unsafe_allow_html=True)
        
        score = lead.get("score", "Unknown").lower()
        badge_class = f"badge-{score}"
        st.markdown(f'<div class="dossier-badge {badge_class}">{score.upper()} LEAD</div>', unsafe_allow_html=True)

        st.divider()

        left, right = st.columns(2)

        with left:
            st.markdown(f'<div class="dossier-section"><div class="section-title">COMPANY INTELLIGENCE</div><p><strong>Signal:</strong> {lead.get("signal", "N/A")}</p><p><strong>Source:</strong> {lead.get("source_url", "N/A")}</p></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="dossier-section"><div class="section-title">WHY THIS LEAD?</div><p>{lead.get("needs_analysis", "No analysis provided.")}</p></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="dossier-section"><div class="section-title">SCORE REASONING</div><p>{lead.get("score_reason", "No reason provided.")}</p></div>', unsafe_allow_html=True)

        with right:
            st.markdown(f'<div class="dossier-section"><div class="section-title">PERSONALIZED OUTREACH</div><div class="outreach-box">{lead.get("outreach_message", "No message generated.")}</div></div>', unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.download_button("Download Transcript", lead.get("outreach_message", ""), file_name=f"{lead.get('company')}_outreach.txt", use_container_width=True)
            
            with c2:
                if st.button("Mark as Contacted", use_container_width=True):
                    st.success("Lead marked!")
            
            with c3:
                # Import the single-lead re-analysis function
                from lead_agent import analyze_and_score_lead, llm  # Accessing the LLM directly
                if st.button("Regenerate", use_container_width=True):
                    with st.spinner("Regenerating outreach..."):
                        try:
                            # Re-run the analysis to get a fresh outreach message
                            new_lead = analyze_and_score_lead(lead, active.get("industry", "General"))
                            lead["outreach_message"] = new_lead.get("outreach_message", "Could not regenerate.")
                            # Update the session state to reflect the new message immediately
                            st.session_state.active_batch["leads"][idx] = lead
                            st.rerun()
                        except Exception as e:
                            st.error(f"Could not regenerate: {e}")

# ============================================================
# ROUTER
# ============================================================
if st.session_state.page == "landing":
    render_landing()
elif st.session_state.page == "prospecting":
    render_prospecting()
elif st.session_state.page == "board":
    render_board()
elif st.session_state.page == "dossier":
    render_dossier()