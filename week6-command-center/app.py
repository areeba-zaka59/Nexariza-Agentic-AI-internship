"""
Nexeriza AI Internship — Week 6
Nexeriza Command Center — Six specialized AI environments.
"""

import streamlit as st
import os, json
from datetime import datetime
from backend import (
    market_research, generate_content, draft_email, summarize_meeting,
    competitor_analysis, monitor_trends, log_activity, load_activity,
)
import plotly.graph_objects as go

st.set_page_config(page_title="Nexeriza Command Center", page_icon="⌘",
                   layout="wide", initial_sidebar_state="collapsed")

if "current_page" not in st.session_state:
    st.session_state.current_page = "home"

LOG_FILE = "activity_log.json"

# ============================================================
# SVG ICONS
# ============================================================
ICONS = {
    "linkedin": '<svg viewBox="0 0 24 24" width="26" height="26" fill="#0A66C2"><path d="M20.5 2h-17A1.5 1.5 0 0 0 2 3.5v17A1.5 1.5 0 0 0 3.5 22h17a1.5 1.5 0 0 0 1.5-1.5v-17A1.5 1.5 0 0 0 20.5 2zM8 19H5v-9h3zM6.5 8.25A1.75 1.75 0 1 1 8.3 6.5a1.78 1.78 0 0 1-1.8 1.75zM19 19h-3v-4.74c0-1.42-.6-1.93-1.38-1.93A1.74 1.74 0 0 0 13 14.19a.66.66 0 0 0 0 .14V19h-3v-9h2.9v1.3a3.11 3.11 0 0 1 2.7-1.4c1.55 0 3.36.86 3.36 3.66z"/></svg>',
    "instagram": '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#E1306C" stroke-width="2"><rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/><circle cx="17.5" cy="6.5" r="1" fill="#E1306C"/></svg>',
    "facebook": '<svg viewBox="0 0 24 24" width="26" height="26" fill="#1877F2"><path d="M22 12a10 10 0 1 0-11.56 9.88v-6.99H7.9V12h2.54V9.8c0-2.5 1.49-3.89 3.77-3.89 1.1 0 2.24.2 2.24.2v2.46h-1.26c-1.24 0-1.63.77-1.63 1.56V12h2.77l-.44 2.89h-2.33v6.99A10 10 0 0 0 22 12z"/></svg>',
    "twitter": '<svg viewBox="0 0 24 24" width="26" height="26" fill="#000"><path d="M18.9 2H22l-7 8 8.2 12h-6.4l-5-7.3L6 22H2.8l7.5-8.6L2.3 2h6.5l4.5 6.6zM17.7 20h1.7L7.4 3.9H5.6z"/></svg>',
    "blog": '<svg viewBox="0 0 24 24" width="26" height="26" fill="none" stroke="#4A6B58" stroke-width="2"><path d="M4 4h16v16H4z"/><path d="M8 8h8M8 12h8M8 16h5"/></svg>',
}

# Per-page background + accent
THEMES = {
    "home":                ("#F7F3EC", "#1F3A2E"),
    "market_research":     ("#EEF3F8", "#143A5C"),
    "content_generation":  ("#FDF2F8", "#8B2E5D"),
    "email_drafting":      ("#F8F0EE", "#8B1A1A"),
    "meeting_summary":     ("#F2F6FA", "#1F4163"),
    "competitor_analysis": ("#EEF0F8", "#2A2E5C"),
    "trend_monitoring":    ("#F2F0F8", "#4A3A7A"),
}
bg, accent = THEMES.get(st.session_state.current_page, THEMES["home"])

# ============================================================
# GLOBAL CSS (theme-aware)
# ============================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Inter:wght@400;500;600;700&family=Playfair+Display:ital,wght@0,500;0,600;0,700;1,500&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"], .stApp * {{ font-family: 'Inter', sans-serif; }}
.stApp {{ background-color: {bg} !important; color: #2B2E2B !important; }}
section[data-testid="stSidebar"] {{ display: none !important; }}
.block-container {{ padding-top: 1.5rem !important; padding-bottom: 3rem; max-width: 1250px; }}
header[data-testid="stHeader"] {{ display: none !important; }}

/* INPUTS */
div[data-testid="stTextInput"] label,
div[data-testid="stTextArea"] label,
div[data-testid="stSelectbox"] label {{
    color: #2B2E2B !important; font-weight: 600 !important; font-size: 13.5px !important;
    -webkit-text-fill-color: #2B2E2B !important;
}}
div[data-testid="stTextInput"] input,
div[data-testid="stTextArea"] textarea,
div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
    background-color: #FFFFFF !important; color: #2B2E2B !important;
    -webkit-text-fill-color: #2B2E2B !important;
    border: 1.5px solid #D9D3C8 !important; border-radius: 10px !important;
    font-size: 15px !important; padding: 10px 14px !important;
}}
div[data-testid="stTextInput"] input::placeholder,
div[data-testid="stTextArea"] textarea::placeholder {{
    color: #A8A093 !important; -webkit-text-fill-color: #A8A093 !important; opacity: 1 !important;
}}
div[data-testid="stTextInput"] > div,
div[data-testid="stTextArea"] > div {{
    background: transparent !important; border: none !important; padding: 0 !important;
}}
div[data-testid="stSelectbox"] div[data-baseweb="select"] span {{
    color: #2B2E2B !important; -webkit-text-fill-color: #2B2E2B !important;
}}

/* BUTTONS */
.stButton button {{
    background: {accent} !important; color: #FFFFFF !important;
    font-weight: 600 !important; border: none !important;
    border-radius: 30px !important; font-size: 14px !important;
    padding: 12px 26px !important; transition: all 0.25s ease !important;
}}
.stButton button:hover {{ transform: translateY(-1px); filter: brightness(1.15); }}
.stDownloadButton button {{
    background: transparent !important; color: {accent} !important;
    border: 1.5px solid {accent} !important; border-radius: 30px !important;
    font-weight: 600 !important; padding: 10px 22px !important;
}}

/* HERO (home) */
.nx-hero-nex {{ font-family: 'Cormorant Garamond', serif; font-weight: 700; font-size: 88px;
    color: #1F3A2E; text-align: center; line-height: 1; margin-bottom: 4px; letter-spacing: 6px; }}
.nx-hero-cmd {{ font-family: 'Cormorant Garamond', serif; font-weight: 700; font-size: 60px;
    color: #1F3A2E; text-align: center; line-height: 1.05; margin-bottom: 22px; letter-spacing: 16px; }}
.nx-hero-author {{ text-align: center; font-size: 14px; color: #4A6B58; letter-spacing: 3px;
    text-transform: uppercase; font-weight: 600; margin-bottom: 12px; }}
.nx-hero-tagline {{ text-align: center; font-size: 16px; color: #7A8A7F; letter-spacing: 1px; margin-bottom: 50px; }}

/* OVAL GATE */
.oval-gate {{
    background: #FFFFFF; border: 1.5px solid #D9D3C8;
    padding: 34px 30px; text-align: center; min-height: 250px;
    display: flex; flex-direction: column; justify-content: center; align-items: center;
    border-radius: 55% 45% 50% 50% / 45% 50% 50% 55%;
    margin-bottom: 12px; transition: all 0.3s ease;
    box-shadow: 0 4px 20px rgba(31,58,46,0.04);
}}
.oval-gate:hover {{ transform: translateY(-6px) scale(1.02);
    box-shadow: 0 16px 44px rgba(31,58,46,0.16); border-color: #1F3A2E; }}
.oval-gate-icon {{ font-size: 52px; margin-bottom: 14px;
    filter: drop-shadow(0 6px 10px rgba(31,58,46,0.18)); }}
.oval-gate-title {{ font-family: 'Cormorant Garamond', serif; font-weight: 700; font-size: 20px;
    letter-spacing: 2px; margin-bottom: 8px; color: #1F3A2E; }}
.oval-gate-desc {{ font-size: 12.5px; line-height: 1.5; max-width: 210px; color: #5A6B60; }}

/* ACTIVITY */
.act-row {{ display: flex; gap: 16px; padding: 14px 0; border-bottom: 1px solid #EFEAE0; align-items: center; }}
.act-row:last-child {{ border-bottom: none; }}
.act-icon {{ width: 42px; height: 42px; border-radius: 50%; display: flex; align-items: center;
    justify-content: center; font-size: 20px; flex-shrink: 0; background: #E6EDE7; }}
.act-tool {{ font-weight: 700; color: #1F3A2E; font-size: 15px; margin-bottom: 3px; }}
.act-input {{ font-size: 13.5px; color: #6B7A6F; margin-bottom: 3px; }}
.act-ts {{ font-size: 11.5px; color: #A8A093; }}

/* FOOTER */
.nx-footer {{ text-align: center; color: #A8A093; font-size: 11.5px; margin-top: 70px;
    letter-spacing: 2px; text-transform: uppercase; }}

/* PAGE HEADER */
.nx-page-title {{ font-family: 'Cormorant Garamond', serif; font-weight: 700; font-size: 54px;
    margin: 0 0 6px 0; line-height: 1.05; letter-spacing: 1px; color: {accent}; }}
.nx-page-sub {{ font-size: 16px; margin-bottom: 30px; color: #5A6B60; }}
.nx-badge {{ display: inline-block; font-size: 11px; font-weight: 700; letter-spacing: 2.5px;
    padding: 6px 16px; border-radius: 24px; text-transform: uppercase; margin-bottom: 14px;
    background: {accent}; color: #FFFFFF; }}

/* JOURNAL */
.journal {{ background: #FBFCFE; border: 1px solid #B8CADB; border-radius: 4px;
    padding: 48px 54px; box-shadow: 0 12px 40px rgba(20,58,92,0.08);
    font-family: 'Playfair Display', serif; }}
.journal::before {{ content: "— NEXERIZA RESEARCH JOURNAL · VOL. 06 —"; display: block;
    text-align: center; font-family: 'JetBrains Mono', monospace; font-size: 11px;
    letter-spacing: 4px; color: #143A5C; margin-bottom: 26px; padding-bottom: 16px;
    border-bottom: 2px double #143A5C; }}
.journal h2 {{ font-family: 'Playfair Display', serif; font-style: italic; font-weight: 500;
    font-size: 24px; color: #143A5C; margin: 26px 0 12px 0; }}
.journal p {{ font-size: 16px; line-height: 1.9; color: #1E2F40; }}
.journal-drop::first-letter {{ font-family: 'Playfair Display', serif; font-size: 64px;
    font-weight: 700; float: left; line-height: 0.9; padding: 4px 10px 0 0; color: #143A5C; }}

/* 3D icon row */
.icon-3d-row {{ display: flex; justify-content: center; gap: 46px; margin: 26px 0; }}
.icon-3d {{ text-align: center; }}
.icon-3d-emoji {{ font-size: 58px; filter: drop-shadow(0 8px 14px rgba(20,58,92,0.25)); }}
.icon-3d-label {{ font-size: 11px; letter-spacing: 2px; color: #4A6B87; margin-top: 6px;
    text-transform: uppercase; font-weight: 600; }}

/* SOCIAL TILES */
.social-grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; margin: 20px 0 28px 0; }}
.social-tile {{ background: #FFFFFF; border: 1.5px solid #F4C9DA; border-radius: 16px;
    padding: 20px 12px; text-align: center; font-size: 13px; font-weight: 600; color: #8B2E5D; }}
.social-tile svg {{ display: block; margin: 0 auto 10px auto; }}

/* EMAIL WINDOW */
.email-window {{ background: #FFFFFF; border: 1px solid #E0CDCD; border-radius: 10px;
    overflow: hidden; box-shadow: 0 12px 40px rgba(139,26,26,0.1); }}
.email-toolbar {{ background: #8B1A1A; color: #FFFFFF; padding: 12px 22px;
    display: flex; justify-content: space-between; align-items: center;
    font-size: 13px; letter-spacing: 1px; }}
.email-toolbar-dots {{ display: flex; gap: 6px; }}
.email-toolbar-dot {{ width: 10px; height: 10px; border-radius: 50%; background: #FFFFFF; opacity: 0.35; }}
.email-meta {{ padding: 20px 32px; border-bottom: 1px solid #F0E2E2; background: #FDFAF9; }}
.email-meta-row {{ display: flex; gap: 12px; font-size: 13.5px; margin-bottom: 6px; }}
.email-meta-label {{ color: #8B1A1A; font-weight: 700; width: 70px; letter-spacing: 1px; }}
.email-meta-value {{ color: #2B2E2B; }}
.email-content {{ padding: 34px 42px; font-family: 'Georgia', serif; font-size: 15.5px;
    line-height: 1.9; color: #1F1F1F; white-space: pre-wrap; }}

/* CALENDAR */
.calendar-card {{ background: #FFFFFF; border: 1px solid #C9D8E6; border-radius: 12px;
    padding: 26px 30px; box-shadow: 0 8px 30px rgba(31,65,99,0.06); margin-bottom: 18px; }}
.calendar-header {{ display: flex; align-items: center; gap: 14px;
    border-bottom: 2px solid #E2B54A; padding-bottom: 14px; margin-bottom: 16px; }}
.calendar-icon {{ background: #1F4163; color: #E2B54A; width: 44px; height: 44px; border-radius: 8px;
    display: flex; align-items: center; justify-content: center; font-size: 22px; }}
.calendar-title {{ font-family: 'Playfair Display', serif; font-size: 20px; font-weight: 700; color: #1F4163; }}
.calendar-sub {{ font-size: 12.5px; color: #6B7A8F; letter-spacing: 1px; }}
.tl-step {{ display: flex; align-items: flex-start; gap: 18px; padding: 14px 0;
    border-bottom: 1px dashed #C9D8E6; }}
.tl-step:last-child {{ border-bottom: none; }}
.tl-marker {{ width: 40px; height: 40px; border-radius: 50%; background: #1F4163; color: #E2B54A;
    display: flex; align-items: center; justify-content: center; font-size: 14px; font-weight: 700;
    flex-shrink: 0; font-family: 'Cormorant Garamond', serif; }}
.tl-title {{ font-weight: 700; color: #1F4163; font-size: 15px; margin-bottom: 3px; }}
.tl-note {{ font-size: 13.5px; color: #4A6B87; line-height: 1.55; }}

/* WAR TABLE */
.war-table {{ width: 100%; border-collapse: collapse; background: #FFFFFF; border-radius: 10px;
    overflow: hidden; box-shadow: 0 8px 30px rgba(42,46,92,0.08); }}
.war-table th {{ background: #2A2E5C; color: #C9A227; padding: 14px 16px; font-size: 12px;
    letter-spacing: 2px; text-transform: uppercase; font-weight: 700; text-align: left; }}
.war-table td {{ padding: 14px 16px; border-bottom: 1px solid #E0E2F0; font-size: 14px;
    color: #2B2E2B; vertical-align: top; }}
.war-table tr:hover td {{ background: #F5F6FC; }}
.war-table tr:last-child td {{ border-bottom: none; }}
.war-table td:first-child {{ color: #2A2E5C; font-weight: 700; }}

/* TREND */
.trend-card {{ background: #FFFFFF; border: 1px solid #D8D0E8; border-radius: 12px;
    padding: 22px 26px; box-shadow: 0 8px 30px rgba(74,58,122,0.06); margin-bottom: 16px; }}
.trend-card-title {{ font-family: 'Cormorant Garamond', serif; font-size: 18px; font-weight: 700;
    color: #4A3A7A; letter-spacing: 1px; margin-bottom: 10px; }}
.sig-card {{ background: #FFFFFF; border: 1px solid #D8D0E8; border-left: 4px solid #8BAE8D;
    border-radius: 8px; padding: 20px 24px; margin-bottom: 12px; }}
.sig-num {{ font-family: 'JetBrains Mono', monospace; font-size: 11px; letter-spacing: 3px;
    color: #6B5C9A; font-weight: 700; text-transform: uppercase; margin-bottom: 6px; }}
.sig-title {{ font-family: 'Cormorant Garamond', serif; font-size: 22px; font-weight: 700;
    color: #4A3A7A; margin-bottom: 6px; line-height: 1.15; }}
.sig-note {{ font-size: 13.5px; color: #5A5A6A; line-height: 1.55; }}
.sig-mom {{ display: inline-block; padding: 3px 12px; border-radius: 20px; font-size: 11.5px;
    font-weight: 700; margin-left: 8px; }}
.mom-rising {{ background: rgba(139,174,141,0.2); color: #3D6B40; }}
.mom-emerging {{ background: rgba(226,181,74,0.2); color: #8A6A0A; }}
.mom-peak {{ background: rgba(107,92,154,0.15); color: #4A3A7A; }}
.mom-declining {{ background: rgba(184,84,84,0.15); color: #8B1A1A; }}
</style>
""", unsafe_allow_html=True)


# ============================================================
# HELPERS
# ============================================================
def go_home():
    if st.button("←  Command Center", key=f"back_{st.session_state.current_page}"):
        st.session_state.current_page = "home"
        st.rerun()


def header(badge_text, title, subtitle):
    go_home()
    st.markdown(f'<span class="nx-badge">{badge_text}</span>', unsafe_allow_html=True)
    st.markdown(f'<div class="nx-page-title">{title}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="nx-page-sub">{subtitle}</div>', unsafe_allow_html=True)


def delete_activity(index):
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                entries = json.load(f)
            if 0 <= index < len(entries):
                entries.pop(index)
                with open(LOG_FILE, "w", encoding="utf-8") as f:
                    json.dump(entries, f, ensure_ascii=False, indent=2)
        except Exception:
            pass


# ============================================================
# HOME
# ============================================================
def render_home():
    st.markdown('<div style="height: 20px;"></div>', unsafe_allow_html=True)
    st.markdown('<div class="nx-hero-nex">NEXERIZA</div>', unsafe_allow_html=True)
    st.markdown('<div class="nx-hero-cmd">COMMAND CENTER</div>', unsafe_allow_html=True)
    st.markdown('<div class="nx-hero-author">Built by Areeba Zaka</div>', unsafe_allow_html=True)
    st.markdown('<div class="nx-hero-tagline">One intelligent workspace. Six business capabilities.</div>', unsafe_allow_html=True)

    gates = [
        ("market_research",     "📊", "MARKET RESEARCH",     "Research and intelligence"),
        ("content_generation",  "🎨", "CONTENT GENERATION",  "Create platform-ready content"),
        ("email_drafting",      "✉️", "EMAIL DRAFTING",      "Professional business communication"),
        ("meeting_summary",     "📅", "MEETING SUMMARY",     "Turn meetings into action"),
        ("competitor_analysis", "⚔️", "COMPETITOR ANALYSIS", "Understand the competitive landscape"),
        ("trend_monitoring",    "📈", "TREND MONITORING",    "Detect emerging market signals"),
    ]
    for row_start in (0, 3):
        cols = st.columns(3, gap="large")
        for i, col in enumerate(cols):
            key, ic, title, desc = gates[row_start + i]
            with col:
                st.markdown(f"""
                <div class="oval-gate">
                    <div class="oval-gate-icon">{ic}</div>
                    <div class="oval-gate-title">{title}</div>
                    <div class="oval-gate-desc">{desc}</div>
                </div>
                """, unsafe_allow_html=True)
                if st.button("Open →", key=f"gate_{key}", use_container_width=True):
                    st.session_state.current_page = key
                    st.rerun()
        st.markdown('<div style="height: 10px;"></div>', unsafe_allow_html=True)

    st.markdown('<div style="height: 40px;"></div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:\'Cormorant Garamond\',serif;font-size:30px;font-weight:700;color:#1F3A2E;letter-spacing:2px;margin-bottom:16px;">Recent Activity</div>', unsafe_allow_html=True)

    entries = load_activity()
    if not entries:
        st.caption("No activity yet — enter a workspace to begin.")
    else:
        icon_map = {"Market Research": "📊", "Content Generation": "🎨", "Email Drafting": "✉️",
                    "Meeting Summary": "📅", "Competitor Analysis": "⚔️", "Trend Monitoring": "📈"}
        page_map = {"Market Research": "market_research", "Content Generation": "content_generation",
                    "Email Drafting": "email_drafting", "Meeting Summary": "meeting_summary",
                    "Competitor Analysis": "competitor_analysis", "Trend Monitoring": "trend_monitoring"}

        indexed = list(enumerate(entries))
        for real_idx, entry in reversed(indexed[-6:]):
            ts = datetime.fromisoformat(entry["timestamp"]).strftime("%b %d · %I:%M %p")
            ic = icon_map.get(entry["tool"], "•")
            c_info, c_open, c_del = st.columns([8, 1, 1])
            with c_info:
                st.markdown(
                    f'<div class="act-row"><div class="act-icon">{ic}</div>'
                    f'<div><div class="act-tool">{entry["tool"]}</div>'
                    f'<div class="act-input">{entry["input"][:70]}</div>'
                    f'<div class="act-ts">{ts}</div></div></div>',
                    unsafe_allow_html=True,
                )
            with c_open:
                if st.button("↗", key=f"open_{real_idx}", help="Reopen this tool"):
                    st.session_state.current_page = page_map.get(entry["tool"], "home")
                    st.rerun()
            with c_del:
                if st.button("✕", key=f"del_{real_idx}", help="Delete"):
                    delete_activity(real_idx)
                    st.rerun()

    st.markdown('<div class="nx-footer">Nexeriza Command Center · Built by Areeba Zaka</div>', unsafe_allow_html=True)


# ============================================================
# 1. MARKET RESEARCH — Blue Journal + 3D icons
# ============================================================
def render_market_research():
    header("📰  Editorial Research Journal", "MARKET RESEARCH", "Turn questions into structured intelligence.")

    st.markdown("""
    <div class="icon-3d-row">
        <div class="icon-3d"><div class="icon-3d-emoji">📖</div><div class="icon-3d-label">Journal</div></div>
        <div class="icon-3d"><div class="icon-3d-emoji">🔍</div><div class="icon-3d-label">Discover</div></div>
        <div class="icon-3d"><div class="icon-3d-emoji">📰</div><div class="icon-3d-label">Briefing</div></div>
    </div>
    """, unsafe_allow_html=True)

    topic = st.text_input("Research Topic", placeholder="e.g. AI agent adoption in healthcare 2026")

    if st.button("Compile Research Journal →") and topic:
        with st.spinner("Writing your research journal..."):
            result = market_research(topic)
        log_activity("Market Research", topic, {"len": len(result["summary"])})

        summary = result["summary"]
        first, rest = (summary[:200], summary[200:]) if len(summary) > 200 else (summary, "")

        st.markdown(f'<div class="journal"><h2>On the Subject of: {topic}</h2>'
                    f'<p class="journal-drop">{first}{rest}</p>', unsafe_allow_html=True)

        if result["sources"]:
            st.markdown('<h2>References & Sources</h2>', unsafe_allow_html=True)
            for s in result["sources"]:
                st.markdown(f"- [{s['title']}]({s['url']})")
        st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# 2. CONTENT GENERATION — Pink studio + real SVG icons
# ============================================================
def render_content_generation():
    header("🎨  Creative Social Studio", "CONTENT GENERATION", "Create platform-ready content from one idea.")

    social_grid_html = (
        '<div class="social-grid">'
        f'<div class="social-tile">{ICONS["linkedin"]}LinkedIn</div>'
        f'<div class="social-tile">{ICONS["instagram"]}Instagram</div>'
        f'<div class="social-tile">{ICONS["facebook"]}Facebook</div>'
        f'<div class="social-tile">{ICONS["twitter"]}X / Twitter</div>'
        f'<div class="social-tile">{ICONS["blog"]}Blog</div>'
        '</div>'
    )
    st.markdown(social_grid_html, unsafe_allow_html=True)

    c1, c2 = st.columns([2, 1])
    with c1:
        topic = st.text_input("Topic", placeholder="e.g. why AI agents matter for SMBs")
    with c2:
        platform = st.selectbox("Target Platform", ["LinkedIn", "Instagram", "Facebook", "X / Twitter", "Blog"])

    c3, c4 = st.columns(2)
    with c3:
        tone = st.selectbox("Tone", ["Professional", "Conversational", "Bold", "Thoughtful"])
    with c4:
        length = st.selectbox("Length", ["Short", "Medium", "Long"])

    if st.button("Generate Content →") and topic:
        with st.spinner("Composing..."):
            content = generate_content(topic)
        log_activity("Content Generation", topic, {"platform": platform})

        if platform == "LinkedIn":
            body = content.get("linkedin", "")
            color = "#0A66C2"
        elif platform == "Instagram":
            body = content.get("instagram", "")
            color = "#E1306C"
        elif platform in ("X / Twitter", "Facebook"):
            body = content.get("twitter", "")
            color = "#000000"
        else:
            body = content.get("linkedin", "")
            color = "#4A6B58"

        st.markdown(f'<div style="background:#FFFFFF;border:1px solid #F4C9DA;'
                    f'border-radius:16px;padding:24px;box-shadow:0 8px 24px rgba(139,46,93,0.08);">'
                    f'<div style="font-weight:700;color:{color};margin-bottom:12px;'
                    f'font-size:14px;letter-spacing:1px;">{platform.upper()} PREVIEW</div>'
                    f'<div style="font-size:15px;line-height:1.7;color:#2B2E2B;white-space:pre-wrap;">{body}</div></div>',
                    unsafe_allow_html=True)
        st.download_button("Download Content", body, file_name="content.txt")


# ============================================================
# 3. EMAIL DRAFTING — Real email window
# ============================================================
def render_email_drafting():
    header("✉️  Executive Correspondence", "EMAIL DRAFTING", "Write clear, persuasive business communication.")

    recipient_label = st.text_input("Recipient", placeholder="e.g. CTO at MediCore Health")
    purpose = st.text_input("Purpose", placeholder="e.g. Follow-up after a discovery call")
    context = st.text_area("Key Points / Context", height=140,
                           placeholder="e.g. They're interested in computer vision...")

    if st.button("Draft Email →") and purpose:
        with st.spinner("Composing correspondence..."):
            email = draft_email(purpose, context)
        log_activity("Email Drafting", purpose, {})

        st.markdown(f'''
        <div class="email-window">
            <div class="email-toolbar">
                <div class="email-toolbar-dots">
                    <div class="email-toolbar-dot"></div>
                    <div class="email-toolbar-dot"></div>
                    <div class="email-toolbar-dot"></div>
                </div>
                <div>DRAFT · NOT SENT</div>
                <div>✉</div>
            </div>
            <div class="email-meta">
                <div class="email-meta-row"><div class="email-meta-label">TO:</div>
                    <div class="email-meta-value">{recipient_label or "—"}</div></div>
                <div class="email-meta-row"><div class="email-meta-label">FROM:</div>
                    <div class="email-meta-value">Areeba Zaka · Nexeriza AI</div></div>
                <div class="email-meta-row"><div class="email-meta-label">SUBJECT:</div>
                    <div class="email-meta-value">{purpose}</div></div>
            </div>
            <div class="email-content">{email}</div>
        </div>
        ''', unsafe_allow_html=True)

        st.download_button("Copy / Download Email", email, file_name="email_draft.txt")


# ============================================================
# 4. MEETING SUMMARY — Calendar layout with real timeline
# ============================================================
def render_meeting_summary():
    header("📅  Productivity Timeline", "MEETING SUMMARY", "Turn conversations into decisions and action.")

    st.markdown('''
    <div class="calendar-card">
        <div class="calendar-header">
            <div class="calendar-icon">📅</div>
            <div>
                <div class="calendar-title">Meeting Input</div>
                <div class="calendar-sub">Paste your raw meeting notes below</div>
            </div>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    notes = st.text_area("Raw Notes", height=200,
                         placeholder="Meeting: Client Strategy\nDate: Sep 14, 2026\nParticipants: Marketing Team, AI Team\n\nRaw Notes:\nDiscussed the new AI automation system...")

    if st.button("Summarize Meeting →") and notes:
        with st.spinner("Structuring your meeting..."):
            result = summarize_meeting(notes)
        log_activity("Meeting Summary", notes[:60], {})

        st.markdown(f'''
        <div class="calendar-card">
            <div class="calendar-header">
                <div class="calendar-icon">✓</div>
                <div><div class="calendar-title">Executive Summary</div>
                <div class="calendar-sub">Auto-extracted from your notes</div></div>
            </div>
            <div class="tl-note" style="font-size:15px;line-height:1.85;">{result.get("summary","")}</div>
        </div>
        ''', unsafe_allow_html=True)

        steps = [
            ("Meeting Started", "Transcript received and parsed"),
            ("Discussion", (result.get("summary","")[:180] + "...") if result.get("summary") else "—"),
            ("Key Decisions", "Extracted from transcript"),
            ("Action Items", f"{len(result.get('action_items', []))} items identified"),
        ]
        st.markdown('<div class="calendar-card"><div class="calendar-header">'
                    '<div class="calendar-icon">⏱</div><div><div class="calendar-title">Timeline</div>'
                    '<div class="calendar-sub">Meeting flow</div></div></div>', unsafe_allow_html=True)
        for i, (label, note) in enumerate(steps, 1):
            st.markdown(f'<div class="tl-step"><div class="tl-marker">{i}</div>'
                        f'<div><div class="tl-title">{label}</div>'
                        f'<div class="tl-note">{note}</div></div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        items = result.get("action_items", [])
        if items:
            rows = ""
            for it in items:
                priority = (it.get('priority', '—') or '—')
                pcolor = {"High": "#8B1A1A", "Medium": "#8A6A0A", "Low": "#3D6B40"}.get(priority, "#4A6B87")
                rows += (
                    f"<tr>"
                    f"<td style='padding:14px 16px;border-bottom:1px solid #E0EAF2;'>{it.get('task','')}</td>"
                    f"<td style='padding:14px 16px;border-bottom:1px solid #E0EAF2;'>{it.get('owner','Unassigned')}</td>"
                    f"<td style='padding:14px 16px;border-bottom:1px solid #E0EAF2;'>{it.get('deadline','TBD')}</td>"
                    f"<td style='padding:14px 16px;border-bottom:1px solid #E0EAF2;'>"
                    f"<span style='background:{pcolor}22;color:{pcolor};padding:4px 12px;border-radius:20px;font-weight:700;font-size:12px;'>{priority}</span>"
                    f"</td>"
                    f"</tr>"
                )

            st.markdown(f'''
            <div class="calendar-card">
                <div class="calendar-header">
                    <div class="calendar-icon">✓</div>
                    <div>
                        <div class="calendar-title">Action Items</div>
                        <div class="calendar-sub">Assigned tasks with owners and deadlines</div>
                    </div>
                </div>
                <table style="width:100%;border-collapse:collapse;font-size:14px;">
                    <thead>
                        <tr>
                            <th style="text-align:left;padding:12px 16px;background:#1F4163;color:#E2B54A;font-size:11px;letter-spacing:2px;text-transform:uppercase;border-radius:8px 0 0 0;">Task</th>
                            <th style="text-align:left;padding:12px 16px;background:#1F4163;color:#E2B54A;font-size:11px;letter-spacing:2px;text-transform:uppercase;">Owner</th>
                            <th style="text-align:left;padding:12px 16px;background:#1F4163;color:#E2B54A;font-size:11px;letter-spacing:2px;text-transform:uppercase;">Deadline</th>
                            <th style="text-align:left;padding:12px 16px;background:#1F4163;color:#E2B54A;font-size:11px;letter-spacing:2px;text-transform:uppercase;border-radius:0 8px 0 0;">Priority</th>
                        </tr>
                    </thead>
                    <tbody>
                        {rows}
                    </tbody>
                </table>
            </div>
            ''', unsafe_allow_html=True)


# ============================================================
# 5. COMPETITOR ANALYSIS — filled comparison table
# ============================================================
def render_competitor_analysis():
    header("⚔️  Strategic Intelligence Room", "COMPETITOR ANALYSIS",
           "Understand the competitive landscape before making your next move.")

    company = st.text_input("Company / Product", placeholder="e.g. Nexeriza AI")

    if st.button("Analyze Landscape →") and company:
        with st.spinner("Mapping competitive landscape..."):
            result = competitor_analysis(company)
        log_activity("Competitor Analysis", company, {})

        comps = result.get("competitors", [])
        c1 = comps[0] if len(comps) > 0 else "Competitor A"
        c2 = comps[1] if len(comps) > 1 else "Competitor B"
        table = result.get("table", {})

        rows = ""
        for factor, row in table.items():
            rows += (f"<tr><td>{factor}</td>"
                     f"<td>{row.get('company','—')}</td>"
                     f"<td>{row.get('comp1','—')}</td>"
                     f"<td>{row.get('comp2','—')}</td></tr>")

        st.markdown(f'''
        <div style="margin-top:18px;">
            <table class="war-table">
                <thead><tr><th>Factor</th><th>{company}</th><th>{c1}</th><th>{c2}</th></tr></thead>
                <tbody>{rows}</tbody>
            </table>
        </div>
        ''', unsafe_allow_html=True)

        def _list(items):
            return "".join([f"<li>{x}</li>" for x in items]) if items else "<li>—</li>"

        st.markdown(f'''
        <div class="calendar-card" style="margin-top:22px;background:#FFFFFF;border-left:4px solid #2A2E5C;">
            <div class="calendar-title" style="color:#2A2E5C;">Strategic Assessment</div>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:16px;">
                <div>
                    <div style="font-weight:700;color:#3D6B40;margin-bottom:8px;">✓ Advantages</div>
                    <ul style="font-size:14px;color:#2B2E2B;line-height:1.7;">{_list(result.get("advantages",[]))}</ul>
                    <div style="font-weight:700;color:#8B1A1A;margin-top:14px;margin-bottom:8px;">✗ Weaknesses</div>
                    <ul style="font-size:14px;color:#2B2E2B;line-height:1.7;">{_list(result.get("weaknesses",[]))}</ul>
                </div>
                <div>
                    <div style="font-weight:700;color:#8A6A0A;margin-bottom:8px;">⚡ Opportunities</div>
                    <ul style="font-size:14px;color:#2B2E2B;line-height:1.7;">{_list(result.get("opportunities",[]))}</ul>
                    <div style="font-weight:700;color:#8B1A1A;margin-top:14px;margin-bottom:8px;">⚠ Threats</div>
                    <ul style="font-size:14px;color:#2B2E2B;line-height:1.7;">{_list(result.get("threats",[]))}</ul>
                </div>
            </div>
            <div style="margin-top:22px;padding-top:18px;border-top:1px solid #E0E2F0;">
                <div style="font-weight:700;color:#2A2E5C;margin-bottom:8px;">Overall Assessment</div>
                <div style="font-size:15px;color:#2B2E2B;line-height:1.75;">{result.get("overall","—")}</div>
            </div>
        </div>
        ''', unsafe_allow_html=True)


# ============================================================
# 6. TREND MONITORING — Real charts
# ============================================================
def render_trend_monitoring():
    header("📈  Live Intelligence Observatory", "TREND MONITORING",
           "Detect movement before it becomes mainstream.")

    industry = st.text_input("Industry / Topic", placeholder="e.g. fintech, healthcare, logistics")

    if st.button("Monitor Trends →") and industry:
        with st.spinner("Scanning live signals..."):
            result = monitor_trends(industry)
        log_activity("Trend Monitoring", industry, {})

        trends = result.get("trends", [])
        if not trends:
            st.warning("No trends found. Try another topic.")
        else:
            names = [t.get("trend", "")[:20] for t in trends]
            momentum = [t.get("momentum", 50) for t in trends]
            shares = [t.get("share", 100/len(trends)) for t in trends]
            growth = [t.get("growth", 0) for t in trends]

            # BAR CHART — momentum
            st.markdown('<div class="trend-card"><div class="trend-card-title">MOMENTUM INDEX · 0-100</div>', unsafe_allow_html=True)
            bar = go.Figure(go.Bar(
                x=names, y=momentum,
                marker_color=["#8BAE8D" if m >= 60 else "#E2B54A" if m >= 40 else "#B85454" for m in momentum],
                text=momentum, textposition="outside",
            ))
            bar.update_layout(height=340, margin=dict(l=10,r=10,t=20,b=40),
                              paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              font=dict(color="#4A3A7A", size=13))
            st.plotly_chart(bar, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

            col_pie, col_growth = st.columns(2)

            # PIE / DONUT — share
            with col_pie:
                st.markdown('<div class="trend-card"><div class="trend-card-title">ATTENTION SHARE</div>', unsafe_allow_html=True)
                pie = go.Figure(go.Pie(
                    labels=names, values=shares, hole=0.55,
                    marker=dict(colors=["#4A3A7A","#8BAE8D","#C9A227","#B85454","#6B5C9A","#A8BFAE"]),
                ))
                pie.update_layout(height=320, margin=dict(l=10,r=10,t=10,b=10),
                                  paper_bgcolor="rgba(0,0,0,0)",
                                  font=dict(color="#4A3A7A", size=12),
                                  showlegend=True)
                st.plotly_chart(pie, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # BAR — growth %
            with col_growth:
                st.markdown('<div class="trend-card"><div class="trend-card-title">GROWTH %</div>', unsafe_allow_html=True)
                grow = go.Figure(go.Bar(
                    x=growth, y=names, orientation="h",
                    marker_color="#4A3A7A", text=[f"{g}%" for g in growth], textposition="outside",
                ))
                grow.update_layout(height=320, margin=dict(l=10,r=10,t=10,b=20),
                                   paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                                   font=dict(color="#4A3A7A", size=12))
                st.plotly_chart(grow, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # Trend cards
            for i, t in enumerate(trends, 1):
                cat = (t.get("category", "Rising") or "Rising").lower()
                mom_class = f"mom-{cat}" if cat in ("rising","emerging","peak","declining") else "mom-rising"
                st.markdown(
                    f'<div class="sig-card"><div class="sig-num">Signal {i:02d} '
                    f'<span class="sig-mom {mom_class}">{t.get("momentum",50)}/100 · {t.get("category","")}</span></div>'
                    f'<div class="sig-title">{t.get("trend","")}</div>'
                    f'<div class="sig-note">{t.get("note","")}</div></div>',
                    unsafe_allow_html=True,
                )

        if result.get("sources"):
            st.markdown('<div class="trend-card"><div class="trend-card-title">LIVE SOURCES</div>', unsafe_allow_html=True)
            for s in result["sources"]:
                st.markdown(f'- [{s["title"]}]({s["url"]})')
            st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
# ROUTER
# ============================================================
RENDERERS = {
    "home": render_home,
    "market_research": render_market_research,
    "content_generation": render_content_generation,
    "email_drafting": render_email_drafting,
    "meeting_summary": render_meeting_summary,
    "competitor_analysis": render_competitor_analysis,
    "trend_monitoring": render_trend_monitoring,
}
RENDERERS[st.session_state.current_page]()