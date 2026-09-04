"""
Nexariza AI Internship — Week 4
The Nexariza Research Desk — Investigative Newsroom UI
"""

import os
import glob
import json
from datetime import datetime, date, timedelta
import streamlit as st
import streamlit.components.v1 as components
from research_engine import (
    agent_researcher,
    agent_analyst,
    agent_writer,
    agent_publisher,
    discover_trending_topic,
)

st.set_page_config(page_title="The Nexariza Research Desk", page_icon="📰", layout="wide")

REPORTS_DIR = "generated_reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

ACADEMIC_DOMAINS = ["arxiv.org", "openai.com", "anthropic.com", ".edu", "microsoft.com/research"]
NEWS_DOMAINS = ["techcrunch.com", "theverge.com", "reuters.com", "bloomberg.com", "wired.com", "venturebeat.com"]

# ============================================================
# STYLING — Investigative Newsroom (FIXED VISIBILITY + INPUT BOX)
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700;800;900&family=PT+Serif:wght@400;700&family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'PT Serif', serif; }
.stApp {
    background-color: #3a3a3a;
    background-image: 
        /* Handwritten-style scribbles - soft */
        radial-gradient(ellipse at 10% 20%, rgba(255,255,255,0.04) 0%, transparent 50%),
        radial-gradient(ellipse at 90% 80%, rgba(255,255,255,0.04) 0%, transparent 50%),
        radial-gradient(ellipse at 50% 50%, rgba(255,255,255,0.02) 0%, transparent 70%),
        /* Random dots like ink splatters - subtle */
        radial-gradient(circle at 15% 45%, rgba(255,255,255,0.06) 1px, transparent 1px),
        radial-gradient(circle at 75% 30%, rgba(255,255,255,0.05) 1px, transparent 1px),
        radial-gradient(circle at 45% 70%, rgba(255,255,255,0.04) 1px, transparent 1px),
        radial-gradient(circle at 85% 55%, rgba(255,255,255,0.05) 1px, transparent 1px),
        radial-gradient(circle at 25% 85%, rgba(255,255,255,0.04) 1px, transparent 1px),
        radial-gradient(circle at 65% 15%, rgba(255,255,255,0.04) 1px, transparent 1px);
    background-size: 
        100% 100%,
        100% 100%,
        100% 100%,
        100% 100%,
        100% 100%,
        100% 100%,
        100% 100%,
        100% 100%,
        100% 100%;
    color: #E8E4D8;
}
/* ===== SIDEBAR - FIXED VISIBILITY ===== */
section[data-testid="stSidebar"] { 
    background: #1a1a1a !important; 
    border-right: 1px solid #3a3a3a;
    padding-top: 20px;
}
section[data-testid="stSidebar"] * { 
    color: #F2EBDA !important; 
    font-family: 'Inter', sans-serif; 
}

/* Sidebar header */
section[data-testid="stSidebar"] .nx6-sidebar-header {
    font-family: 'Playfair Display', serif;
    font-weight: 700;
    font-size: 22px;
    color: #F2EBDA !important;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 2px solid #3A3A40;
}

/* Sidebar clipping cards - CLEAN VERSION (no zig-zag) */
section[data-testid="stSidebar"] .nx6-clip {
    background: #2A2A30 !important;
    border: 1px solid #4A4A50;
    border-radius: 4px;
    padding: 14px 16px;
    padding-right: 35px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.2);
    position: relative;
    transition: all 0.2s ease;
    margin-bottom: 12px;
    transform: rotate(0deg) !important;
}
section[data-testid="stSidebar"] .nx6-clip:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    border-color: #8C1B24;
}
section[data-testid="stSidebar"] .nx6-clip-date {
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    letter-spacing: 1px;
    color: #A39B87 !important;
    text-transform: uppercase;
}
section[data-testid="stSidebar"] .nx6-clip-title {
    font-family: 'Playfair Display', serif;
    font-size: 16px;
    color: #F2EBDA !important;
    margin: 6px 0;
}
section[data-testid="stSidebar"] .nx6-clip-meta {
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    color: #A39B87 !important;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
section[data-testid="stSidebar"] .nx6-clip-filed {
    font-size: 9px;
    font-weight: 800;
    color: #6B8C6E !important;
    letter-spacing: 1px;
    border: 1px solid #6B8C6E;
    padding: 2px 8px;
    border-radius: 2px;
    transform: rotate(0deg) !important;
}

/* Sidebar buttons */
section[data-testid="stSidebar"] .stButton button {
    background: transparent !important;
    border: none !important;
    text-align: left !important;
    font-weight: 400 !important;
    padding: 0 !important;
    color: #F2EBDA !important;
    font-size: 12px !important;
    font-family: 'Inter', sans-serif !important;
    text-decoration: underline !important;
}
section[data-testid="stSidebar"] .stButton button:hover {
    color: #8C1B24 !important;
}

/* ===== TEXT INPUT - COMPLETELY FIXED ===== */
/* Remove ALL extra boxes and borders */
div[data-testid="stTextInput"] {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
}
div[data-testid="stTextInput"] > div {
    border: 2px solid #3A3A40 !important;
    border-radius: 2px !important;
    background: #2a2a2a !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.3) !important;
    padding: 0 !important;
    margin: 0 !important;
}
div[data-testid="stTextInput"] > div > div {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
    padding: 0 !important;
    margin: 0 !important;
}
div[data-testid="stTextInput"] > div > div > input {
    border: none !important;
    box-shadow: none !important;
    background: #3a3a3a !important;
    color: #E8E4D8 !important;
    -webkit-text-fill-color: #E8E4D8 !important;
    font-family: 'PT Serif', serif !important;
    font-size: 18px !important;
    padding: 14px 18px !important;
    margin: 0 !important;
    width: 100% !important;
    outline: none !important;
}
div[data-testid="stTextInput"] > div > div > input:focus {
    border: none !important;
    box-shadow: none !important;
    outline: none !important;
}
div[data-testid="stTextInput"] > div > div > input::placeholder {
    color: #9A9384 !important;
    font-style: italic;
}

/* ---- MASTHEAD - LARGER ---- */
.nx6-masthead { 
    font-family: 'Playfair Display', serif; 
    font-weight: 900; 
    font-size: 56px; 
    text-align: center; 
    margin: 4px 0 2px 0;
    letter-spacing: -1px;
    color: #E8E4D8;
}
.nx6-tagline { 
    font-family: 'PT Serif', serif; 
    font-style: italic; 
    text-align: center; 
    color: #B0ACA4; 
    font-size: 16px; 
    margin-bottom: 6px;
}
.nx6-dateline { 
    text-align: center; 
    font-family: 'Inter', sans-serif; 
    font-size: 13px; 
    letter-spacing: 1.5px; 
    color: #B0ACA4; 
    text-transform: uppercase;
    border-top: 2px solid #4a4a4a; 
    border-bottom: 1px solid #4a4a4a; 
    padding: 8px 0; 
    margin: 10px 0 28px 0; 
}

/* ---- Assignment Section - LARGER ---- */
.nx6-assign-title { 
    font-family: 'Playfair Display', serif; 
    font-weight: 700; 
    font-size: 28px; 
    margin-bottom: 2px; 
    color: #E8E4D8;
}
.nx6-assign-sub { 
    font-family: 'PT Serif', serif; 
    font-style: italic; 
    color: #B0ACA4; 
    font-size: 16px; 
    margin-bottom: 16px; 
}

/* ---- Newsroom Pipeline - LARGER & READABLE ---- */
.nx6-desk-num { 
    font-family: 'Inter', sans-serif; 
    font-size: 28px; 
    font-weight: 800; 
    color: #D8CBAE; 
}
.nx6-desk-label { 
    font-family: 'Inter', sans-serif; 
    font-size: 15px; 
    letter-spacing: 1.5px; 
    font-weight: 700; 
    text-transform: uppercase; 
    color: #E8E4D8; 
    margin-top: 4px; 
}
.nx6-desk-status { 
    font-family: 'Inter', sans-serif; 
    font-size: 14px; 
    letter-spacing: 0.8px; 
    margin-top: 10px; 
    text-transform: uppercase; 
    font-weight: 600; 
}
.nx6-desk-status.idle { color: #8A8580; }
.nx6-desk-status.working { color: #E8454A; }
.nx6-desk-status.done { color: #4CAF50; }
.nx6-desk-info { 
    font-family: 'PT Serif', serif; 
    font-size: 14px; 
    color: #B0ACA4; 
    margin-top: 8px; 
    min-height: 20px; 
}

/* ---- Article Styling - LARGER ---- */
.nx6-headline { 
    font-family: 'Playfair Display', serif; 
    font-weight: 800; 
    font-size: 42px; 
    line-height: 1.15; 
    margin: 8px 0 12px 0; 
    color: #E8E4D8;
}
.nx6-byline { 
    font-family: 'Inter', sans-serif; 
    font-size: 14px; 
    color: #B0ACA4; 
    border-bottom: 2px solid #4a4a4a; 
    padding-bottom: 14px; 
    margin-bottom: 20px; 
}
.nx6-article-body {
    color: #D0CCC4;
    font-size: 17px;
    line-height: 1.7;
}
.nx6-article-body h2 {
    color: #E8E4D8;
    font-size: 28px;
}
.nx6-article-body h3 {
    color: #E8E4D8;
    font-size: 22px;
}
.nx6-pullquote { 
    border-left: 4px solid #E8454A; 
    padding: 6px 0 6px 18px; 
    margin: 20px 0; 
    font-family: 'Playfair Display', serif;
    font-style: italic; 
    font-size: 22px; 
    color: #D0CCC4; 
}
.nx6-editornote { 
    background: rgba(60, 60, 60, 0.5); 
    border: 1px dashed #4A4A50; 
    border-radius: 2px; 
    padding: 16px 20px; 
    margin: 18px 0;
    font-family: 'Inter', sans-serif; 
    font-size: 14px; 
    color: #C0BCB4; 
}

/* ---- Source Room - LARGER ---- */
.nx6-src-title { 
    font-family: 'PT Serif', serif; 
    font-size: 16px; 
    color: #E8E4D8; 
    margin-top: 4px; 
}
.nx6-src-domain { 
    font-family: 'Inter', sans-serif; 
    font-size: 13px; 
    color: #8A8580; 
}

/* ---- Timeline - LARGER ---- */
.nx6-timeline-label { 
    font-family: 'Inter', sans-serif; 
    font-size: 15px; 
    font-weight: 600; 
    color: #E8E4D8; 
}
.nx6-timeline-time { 
    font-family: 'Inter', sans-serif; 
    font-size: 13px; 
    color: #8A8580; 
}

/* ---- Eyebrow - LARGER ---- */
.nx6-eyebrow { 
    font-family: 'Inter', sans-serif; 
    letter-spacing: 3px; 
    font-size: 13px; 
    font-weight: 700; 
    color: #E8454A; 
    text-transform: uppercase;
    margin-top: 28px;
}

/* ---- Press Room - LARGER ---- */
.nx6-press-title {
    font-family: 'Playfair Display', serif; 
    font-weight: 700; 
    font-size: 17px; 
    margin-bottom: 8px;
    color: #E8E4D8;
}

/* ---- Assignment Section ---- */
.nx6-assign-title { 
    font-family: 'Playfair Display', serif; 
    font-weight: 700; 
    font-size: 24px; 
    margin-bottom: 2px; 
    color: #E8E4D8;
}
.nx6-assign-sub { 
    font-family: 'PT Serif', serif; 
    font-style: italic; 
    color: #9A9384; 
    font-size: 14px; 
    margin-bottom: 16px; 
}
/* ---- Newsroom Pipeline ---- */
.nx6-desk-num { 
    font-family: 'Inter', sans-serif; 
    font-size: 20px; 
    font-weight: 800; 
    color: #D8CBAE; 
}
.nx6-desk-label { 
    font-family: 'Inter', sans-serif; 
    font-size: 12px; 
    letter-spacing: 1.5px; 
    font-weight: 700; 
    text-transform: uppercase; 
    color: #1B1B1F; 
    margin-top: 2px; 
}
.nx6-desk-status { 
    font-family: 'Inter', sans-serif; 
    font-size: 11px; 
    letter-spacing: 0.8px; 
    margin-top: 8px; 
    text-transform: uppercase; 
    font-weight: 600; 
}
.nx6-desk-status.idle { color: #6B6558; }
.nx6-desk-status.working { color: #8C1B24; }
.nx6-desk-status.done { color: #4CAF50; }
.nx6-desk-info { 
    font-family: 'PT Serif', serif; 
    font-size: 12.5px; 
    color: #9A9384; 
    margin-top: 6px; 
    min-height: 18px; 
}
.nx6-desk-dot { 
    width: 7px; 
    height: 7px; 
    border-radius: 50%; 
    background: #8C1B24; 
    display: inline-block; 
    margin-right: 6px; 
    animation: nx6-pulse 1s infinite; 
}
@keyframes nx6-pulse { 
    0%,100%{opacity:1;} 
    50%{opacity:0.2;} 
}

/* ---- Article Styling ---- */
.nx6-torn { 
    position: relative; 
    margin-top: 12px;
}
/* Removed the torn paper edge effect */
.nx6-stamp { 
    display: inline-block; 
    font-family: 'Inter', sans-serif; 
    font-size: 11px; 
    font-weight: 800; 
    letter-spacing: 1.5px;
    color: #FFFFFF !important; 
    background: #8C1B24;
    border: 1.5px solid #8C1B24; 
    padding: 4px 14px; 
    border-radius: 3px; 
    transform: rotate(-2deg); 
    text-transform: uppercase; 
    box-shadow: 0 2px 8px rgba(140, 27, 36, 0.3);
}
.nx6-headline { 
    font-family: 'Playfair Display', serif; 
    font-weight: 800; 
    font-size: 36px; 
    line-height: 1.15; 
    margin: 8px 0 12px 0; 
    color: #E8E4D8;
}
.nx6-byline { 
    font-family: 'Inter', sans-serif; 
    font-size: 12.5px; 
    color: #6B6558; 
    border-bottom: 2px solid #1B1B1F; 
    padding-bottom: 14px; 
    margin-bottom: 20px; 
}
.nx6-article-body {
    color: #D0CCC4;
}
.nx6-article-body h2 {
    color: #E8E4D8;
}
.nx6-article-body h3 {
    color: #E8E4D8;
}
.nx6-article-body h2 { 
    font-family: 'Playfair Display', serif; 
    font-size: 23px; 
    margin-top: 28px; 
    border-top: 1px solid #D8D0BE; 
    padding-top: 20px; 
}
.nx6-article-body h3 { 
    font-family: 'Playfair Display', serif; 
    font-size: 18px; 
    margin-top: 18px; 
}
.nx6-pullquote { 
    border-left: 4px solid #8C1B24; 
    padding: 6px 0 6px 18px; 
    margin: 20px 0; 
    font-family: 'Playfair Display', serif;
    font-style: italic; 
    font-size: 19px; 
    color: #D0CCC4; 
}
.nx6-editornote { 
    background: rgba(60, 60, 60, 0.5); 
    border: 1px dashed #4A4A50; 
    border-radius: 2px; 
    padding: 14px 18px; 
    margin: 18px 0;
    font-family: 'Inter', sans-serif; 
    font-size: 12.5px; 
    color: #B0ACA4; 
}
.nx6-editornote b { color: #8C1B24; }

/* ---- Source Room ---- */
.nx6-src-card { 
    border-bottom: 1px solid #E3DCC9; 
    padding: 12px 0; 
}
.nx6-src-tag { 
    font-family: 'Inter', sans-serif; 
    font-size: 9.5px; 
    font-weight: 700; 
    letter-spacing: 1px; 
    text-transform: uppercase;
    padding: 2px 8px; 
    border-radius: 2px; 
    margin-right: 6px; 
}
.nx6-src-tag.academic { background: #E6EFE7; color: #2E6B3E; }
.nx6-src-tag.news { background: #FBE9E4; color: #8C1B24; }
.nx6-src-tag.primary { background: #EFEAF7; color: #5B4A8C; }
.nx6-src-title { 
    font-family: 'PT Serif', serif; 
    font-size: 14px; 
    color: #E8E4D8; 
    margin-top: 4px; 
}
.nx6-src-domain { 
    font-family: 'Inter', sans-serif; 
    font-size: 11px; 
    color: #6B6558; 
}
.nx6-src-card { 
    border-bottom: 1px solid #2a2a2a; 
    padding: 12px 0; 
}
/* ---- Timeline ---- */
.nx6-timeline-item { 
    display: flex; 
    gap: 14px; 
    margin-bottom: 14px; 
    padding: 8px 12px;
    background: rgba(40, 40, 40, 0.6);
    border-radius: 2px;
    border-left: 3px solid #8C1B24;
}
.nx6-timeline-label { 
    font-family: 'Inter', sans-serif; 
    font-size: 13px; 
    font-weight: 600; 
    color: #E8E4D8; 
}
.nx6-timeline-time { 
    font-family: 'Inter', sans-serif; 
    font-size: 11px; 
    color: #6B6558; 
}
.nx6-timeline-dot { 
    width: 10px; 
    height: 10px; 
    border-radius: 50%; 
    background: #8C1B24; 
    margin-top: 4px; 
    flex-shrink: 0; 

/* ---- Buttons ---- */
.stButton button, .stFormSubmitButton button, div[data-testid="stDownloadButton"] button {
    background: #1B1B1F !important; 
    color: #FFFFFF !important; 
    -webkit-text-fill-color: #FFFFFF !important;
    font-family: 'Inter', sans-serif !important; 
    font-weight: 700 !important; 
    border-radius: 2px !important;
    border: 1px solid #1B1B1F !important; 
    font-size: 12.5px !important; 
    letter-spacing: 0.8px !important;
    text-transform: uppercase !important; 
    transition: all 0.2s ease !important;
    padding: 8px 16px !important;
}
.stButton button:hover, .stFormSubmitButton button:hover, div[data-testid="stDownloadButton"] button:hover {
    background: #8C1B24 !important; 
    border-color: #8C1B24 !important; 
    color: #FFFFFF !important; 
    -webkit-text-fill-color: #FFFFFF !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}
.stButton button p, .stFormSubmitButton button p, div[data-testid="stDownloadButton"] button p { 
    color: #FFFFFF !important; 
    -webkit-text-fill-color: #FFFFFF !important; 
}

/* --- Container Styling --- */
div[data-testid="stContainer"] {
    border: 1px solid #4a4a4a;
    border-radius: 2px;
    padding: 24px;
    background: rgba(60, 60, 60, 0.95);
    margin-top: 12px;
}
div[data-baseweb="input"] {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
}
div[data-baseweb="base-input"] {
    border: none !important;
    box-shadow: none !important;
    background: transparent !important;
}

div[data-testid="stTextInput"] input {
    -webkit-appearance: none !important;
}

[data-testid="stSidebarCollapseButton"] {
    display: none !important;
}
[data-testid="stSidebarCollapseButton"] svg {
    display: none !important;
}
</style>
""", unsafe_allow_html=True)


def classify_source(url: str) -> str:
    for d in ACADEMIC_DOMAINS:
        if d in url:
            return "academic"
    for d in NEWS_DOMAINS:
        if d in url:
            return "news"
    return "primary"


def render_desk_strip(stage: int, info: dict):
    """stage: -1 idle, 0..3 desk working, 4 all done. info: dict with counts for done desks."""
    desks = [
        ("01", "Research Desk", "Investigating", info.get("sources")),
        ("02", "Analyst Desk", "Cross-Referencing", info.get("insights")),
        ("03", "Writer's Desk", "Composing", info.get("words")),
        ("04", "Publishing Desk", "Ready for Press", info.get("editions")),
    ]
    cols = st.columns(4)
    for i, (col, (num, name, working_word, live_info)) in enumerate(zip(cols, desks)):
        if stage > i or stage >= 4:
            status, cls, dot = "Filed", "done", ""
        elif stage == i:
            status, cls, dot = working_word, "working", '<span class="nx6-desk-dot"></span>'
        else:
            status, cls, dot = "Standing By", "idle", ""
        info_text = live_info if (stage > i or stage >= 4) and live_info else ""
        html = (
            f'<div class="nx6-desk-num">{num}</div>'
            f'<div class="nx6-desk-label">{name}</div>'
            f'<div class="nx6-desk-status {cls}">{dot}{status}</div>'
            f'<div class="nx6-desk-info">{info_text}</div>'
        )
        with col:
            st.markdown(html, unsafe_allow_html=True)


def load_all_reports():
    reports = []
    for fpath in sorted(glob.glob(f"{REPORTS_DIR}/*.json"), key=os.path.getmtime, reverse=True):
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
                data["_path"] = fpath
                reports.append(data)
        except (json.JSONDecodeError, KeyError):
            continue
    return reports


def date_label(ts):
    d = ts.date()
    today = date.today()
    if d == today:
        return "TODAY"
    if d == today - timedelta(days=1):
        return "YESTERDAY"
    return d.strftime("%B %d").upper()


def delete_report(file_path):
    """Delete a report file and return True if successful"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as e:
        st.error(f"Error deleting report: {e}")
    return False


# ============================================================
# SESSION STATE
# ============================================================
if "active_report" not in st.session_state:
    st.session_state.active_report = None
if "pipeline_stage" not in st.session_state:
    st.session_state.pipeline_stage = -1
if "desk_info" not in st.session_state:
    st.session_state.desk_info = {}
if "delete_trigger" not in st.session_state:
    st.session_state.delete_trigger = False

# ============================================================
# SIDEBAR — THE ARCHIVE (with delete buttons)
# ============================================================
with st.sidebar:
    st.markdown('<div style="font-family: \'Inter\', sans-serif; letter-spacing: 3px; font-size: 11px; font-weight: 700; color: #8C1B24; text-transform: uppercase;">NEXARIZA AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="nx6-sidebar-header">The Archive</div>', unsafe_allow_html=True)

    reports = load_all_reports()
    
    if st.session_state.delete_trigger:
        st.session_state.delete_trigger = False
        st.rerun()
    
    if not reports:
        st.caption("📭 No issues filed yet.")
    else:
        for r in reports:
            ts = datetime.fromtimestamp(os.path.getmtime(r["_path"]))
            title = r["topic"] if len(r["topic"]) <= 34 else r["topic"][:31] + "..."
            src_count = len(r.get("sources", []))
            report_key = r["_path"]
            
            col1, col2 = st.columns([10, 1])
            with col1:
                clip_html = (
                    '<div class="nx6-clip">'
                    f'<div class="nx6-clip-date">{date_label(ts)} · {ts.strftime("%H:%M")}</div>'
                    f'<div class="nx6-clip-title">{title}</div>'
                    f'<div class="nx6-clip-meta"><span>{src_count} sources</span><span class="nx6-clip-filed">FILED</span></div>'
                    '</div>'
                )
                st.markdown(clip_html, unsafe_allow_html=True)
                
                if st.button("📄 Open clipping", key=f"open_{report_key}", use_container_width=True):
                    st.session_state.active_report = r
                    st.session_state.pipeline_stage = 4
                    st.rerun()
            
            with col2:
                if st.button("✕", key=f"delete_{report_key}", help="Delete this report"):
                    if delete_report(report_key):
                        if st.session_state.active_report and st.session_state.active_report.get("_path") == report_key:
                            st.session_state.active_report = None
                            st.session_state.pipeline_stage = -1
                            st.session_state.desk_info = {}
                        st.session_state.delete_trigger = True
                        st.rerun()

# ============================================================
# MASTHEAD
# ============================================================
issue_number = len(load_all_reports()) + (0 if st.session_state.active_report else 1)
current_date = datetime.now().strftime("%A, %B %d, %Y")

st.markdown('<div class="nx6-masthead">THE NEXARIZA RESEARCH DESK</div>', unsafe_allow_html=True)
st.markdown('<div class="nx6-tagline">Multi-Agent Intelligence, Delivered.</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="nx6-dateline">{current_date} &nbsp;·&nbsp; Issue No. {issue_number} &nbsp;·&nbsp; Nexariza AI Agentic Systems</div>',
    unsafe_allow_html=True,
)

# ============================================================
# ASSIGNMENT SECTION
# ============================================================
st.markdown('<div class="nx6-assign-title">📋 Assign a Story</div>', unsafe_allow_html=True)
st.markdown('<div class="nx6-assign-sub">What should the newsroom investigate today?</div>', unsafe_allow_html=True)

with st.form(key="assign_form", clear_on_submit=False):
    c1, c2 = st.columns([5, 1.6])
    with c1:
        topic_input = st.text_input(
            "Story assignment", 
            placeholder="Enter your research topic here...", 
            label_visibility="collapsed"
        )
    with c2:
        commission_clicked = st.form_submit_button("FILE ASSIGNMENT →", use_container_width=True)
components.html("""
<script>
setTimeout(function() {
    const doc = window.parent.document;
    const inputs = doc.querySelectorAll('input[type="text"]');
    inputs.forEach(function(inp) {
        inp.setAttribute('autocomplete', 'off');
        inp.setAttribute('autocorrect', 'off');
        inp.setAttribute('autocapitalize', 'off');
        inp.setAttribute('spellcheck', 'false');
    });
}, 300);
</script>
""", height=0)
desk_strip_slot = st.empty()
with desk_strip_slot.container():
    render_desk_strip(
        st.session_state.pipeline_stage if st.session_state.active_report else -1,
        st.session_state.desk_info,
    )

# ============================================================
# PIPELINE EXECUTION
# ============================================================
if commission_clicked:
    if topic_input.strip():
        topic = topic_input.strip()
    else:
        with st.spinner("No topic given — the newsroom is scouting a fresh story..."):
            topic = discover_trending_topic()

    timeline = {"📋 Assignment received": datetime.now().strftime("%H:%M:%S")}

    timeline["🔍 Research started"] = datetime.now().strftime("%H:%M:%S")
    with desk_strip_slot.container():
        render_desk_strip(0, {})
    research = agent_researcher(topic)
    src_count = len(research["sources"])
    timeline[f"📚 Sources collected ({src_count})"] = f"{datetime.now().strftime('%H:%M:%S')}"
    st.session_state.desk_info["sources"] = f"{src_count} sources collected"

    with desk_strip_slot.container():
        render_desk_strip(1, st.session_state.desk_info)
    analysis = agent_analyst(research)
    insight_count = len(analysis.get("key_insights", []))
    timeline[f"💡 Analysis completed ({insight_count} insights)"] = f"{datetime.now().strftime('%H:%M:%S')}"
    st.session_state.desk_info["insights"] = f"{insight_count} insights identified"

    with desk_strip_slot.container():
        render_desk_strip(2, st.session_state.desk_info)
    timeline["✍️ Writing started"] = datetime.now().strftime("%H:%M:%S")
    report_text = agent_writer(topic, analysis)
    word_count = len(report_text.split())
    st.session_state.desk_info["words"] = f"{word_count} words drafted"

    with desk_strip_slot.container():
        render_desk_strip(3, st.session_state.desk_info)
    published = agent_publisher(topic, report_text)
    timeline["✅ Report approved"] = datetime.now().strftime("%H:%M:%S")
    st.session_state.desk_info["editions"] = "2 editions ready"

    result = {
        "topic": topic,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "sources": research["sources"],
        "analysis": analysis,
        "full_report": report_text,
        "linkedin_post": published["linkedin"],
        "medium_post": published["medium"],
        "timeline": timeline,
    }
    fname = f"{REPORTS_DIR}/report_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.json"
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    result["_path"] = fname

    st.session_state.active_report = result
    st.session_state.pipeline_stage = 4

    with desk_strip_slot.container():
        render_desk_strip(4, st.session_state.desk_info)
    
    st.rerun()

# ============================================================
# THE INVESTIGATION — Timeline
# ============================================================
active = st.session_state.active_report
if active and active.get("timeline"):
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="nx6-eyebrow">⏳ The Investigation</div>', unsafe_allow_html=True)
    with st.container():
        for label, ts in active["timeline"].items():
            item_html = (
                '<div class="nx6-timeline-item">'
                '<div class="nx6-timeline-dot"></div>'
                f'<div><div class="nx6-timeline-label">{label}</div>'
                f'<div class="nx6-timeline-time">{ts}</div></div>'
                '</div>'
            )
            st.markdown(item_html, unsafe_allow_html=True)

# ============================================================
# THE ARTICLE
# ============================================================
if active:
    st.markdown("<br>", unsafe_allow_html=True)
    with st.container():
        # st.markdown('<div class="nx6-torn"></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([1, 10])
        with col1:
            st.markdown('<span class="nx6-stamp">Special Report</span>', unsafe_allow_html=True)
        with col2:
            st.markdown('<span class="nx6-stamp" style="background: #2E6B3E; border-color: #2E6B3E; color: #FFFFFF !important;">Verified ✓</span>', unsafe_allow_html=True)
        
        st.markdown(f'<div class="nx6-headline">{active["topic"]}</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="nx6-byline">By the Nexariza AI Research Desk &nbsp;·&nbsp; {active.get("date","")} &nbsp;·&nbsp; {len(active.get("sources",[]))} sources consulted</div>',
            unsafe_allow_html=True,
        )

        insights = active.get("analysis", {}).get("key_insights", [])
        if insights:
            st.markdown(f'<div class="nx6-pullquote">"{insights[0]}"</div>', unsafe_allow_html=True)

        trends = active.get("analysis", {}).get("trends", "")
        if trends:
            st.markdown(
                f'<div class="nx6-editornote"><b>📝 Field Note —</b> {trends}</div>',
                unsafe_allow_html=True,
            )

        st.markdown('<div class="nx6-article-body">', unsafe_allow_html=True)
        st.markdown(active["full_report"])
        st.markdown('</div>', unsafe_allow_html=True)

        if len(insights) > 1:
            st.markdown(f'<div class="nx6-pullquote">"{insights[-1]}"</div>', unsafe_allow_html=True)

    # ---- THE SOURCE ROOM ----
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="nx6-eyebrow">📚 The Source Room</div>', unsafe_allow_html=True)
    with st.container():
        sources = active.get("sources", [])
        academic_n = sum(1 for s in sources if classify_source(s.get("url", "")) == "academic")
        news_n = sum(1 for s in sources if classify_source(s.get("url", "")) == "news")
        primary_n = len(sources) - academic_n - news_n
        st.caption(f"📊 {len(sources)} sources consulted — {academic_n} academic · {news_n} news · {primary_n} primary/industry")
        st.caption("ℹ️ Classified by domain — a heuristic, not a verified fact-check")
        
        for src in sources[:14]:
            tag = classify_source(src.get("url", ""))
            tag_label = {"academic": "Academic", "news": "News", "primary": "Primary"}[tag]
            domain = src.get("url", "").split("/")[2] if "://" in src.get("url", "") else src.get("url", "")
            card_html = (
                '<div class="nx6-src-card">'
                f'<span class="nx6-src-tag {tag}">{tag_label}</span>'
                f'<div class="nx6-src-title">{src.get("title","")}</div>'
                f'<div class="nx6-src-domain">{domain}</div>'
                '</div>'
            )
            st.markdown(card_html, unsafe_allow_html=True)

    # ---- THE PRESS ROOM ----
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="nx6-eyebrow">📰 The Press Room</div>', unsafe_allow_html=True)
    pcol1, pcol2, pcol3 = st.columns(3)
    
    with pcol1:
        with st.container():
            st.markdown('<div style="font-family: \'Playfair Display\', serif; font-weight: 700; font-size: 15px; margin-bottom: 8px;">LinkedIn — Social Edition</div>', unsafe_allow_html=True)
            st.caption(active["linkedin_post"][:140] + "...")
            st.download_button("📤 Send to Press", active["linkedin_post"], file_name="linkedin_post.txt", use_container_width=True, key="dl_li")
    
    with pcol2:
        with st.container():
            st.markdown('<div style="font-family: \'Playfair Display\', serif; font-weight: 700; font-size: 15px; margin-bottom: 8px;">Medium — Long Form Edition</div>', unsafe_allow_html=True)
            st.caption(active["medium_post"][:140] + "...")
            st.download_button("📝 Publish Edition", active["medium_post"], file_name="medium_post.txt", use_container_width=True, key="dl_med")
    
    with pcol3:
        with st.container():
            st.markdown('<div style="font-family: \'Playfair Display\', serif; font-weight: 700; font-size: 15px; margin-bottom: 8px;">Full Report — Archive Edition</div>', unsafe_allow_html=True)
            st.caption(active["full_report"][:140] + "...")
            st.download_button("📦 Archive Report", active["full_report"], file_name="full_report.txt", use_container_width=True, key="dl_full")

# ---- Footer ----
st.markdown('<div style="text-align:center; color:#9A9384; font-family: Inter, sans-serif; font-size: 11px; margin-top: 44px; letter-spacing: 1px; padding-bottom: 20px;">🏛️ BUILT BY AREEBA ZAKA — NEXARIZA AI AGENTIC AI INTERNSHIP</div>', unsafe_allow_html=True)