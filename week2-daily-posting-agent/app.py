"""
Nexariza AI Internship — Week 2
NEXA // CONTENT ENGINE — AI Research Workspace
"""

import os
import json
import glob
import time
from datetime import datetime, date, timedelta
import streamlit as st

from daily_posting_agent import (
    research_topic,
    generate_linkedin_post,
    generate_instagram_caption,
    generate_twitter_thread,
    save_daily_report,
)

st.set_page_config(page_title="NEXA // Content Engine", page_icon="◆", layout="wide")

# ============================================================
# STYLING
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700;800&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; font-size: 15px; }

.stApp {
    background: #FFF8E1;
    color: #3B2C24;
}
section[data-testid="stSidebar"] {
    background: #FFF1D0;
    border-right: 1px solid #F0DFC0;
}
div[data-testid="stAlert"] {
    background: #FFFDF6 !important;
    border: 1px solid #E86FA0 !important;
    border-radius: 10px !important;
}
div[data-testid="stAlert"] p {
    color: #3B2C24 !important;
    font-weight: 500 !important;
}

div[data-testid="stPopover"] button {
    background: #FFFDF6 !important;
    color: #D9518B !important;
    font-weight: 700 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    border: 2px solid #F49CC4 !important;
    border-radius: 999px !important;
    box-shadow: none !important;
}
div[data-testid="stPopover"] button:hover {
    background: #FBE4EF !important;
    transform: translateY(-1px);
}

.nx-eyebrow {
    font-family: 'Space Grotesk', sans-serif; letter-spacing: 1.5px; font-size: 13px;
    color: #D9518B; text-transform: uppercase; margin: 22px 0 10px 0; font-weight: 800;
}
.nx-eyebrow:first-child { margin-top: 0; }
.nx-title {
    font-family: 'Space Grotesk', sans-serif; font-weight: 800; font-size: 36px;
    background: linear-gradient(90deg, #F49CC4 0%, #E86FA0 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    -webkit-text-stroke: 0.5px #E86FA0;
    margin-bottom: 2px;
}
.nx-sub { color: #8A7562; font-size: 14px; margin-bottom: 26px; }

/* ---- Command capsule ---- */
div[data-testid="stForm"] {
    background: #FFFDF6 !important;
    border: 1px solid #F0DFC0 !important;
    border-radius: 999px !important;
    padding: 8px 10px 8px 22px !important;
    box-shadow: 0 6px 18px rgba(232,111,160,0.08);
}
div[data-testid="stForm"]:focus-within {
    border-color: #E86FA0 !important;
    box-shadow: 0 0 0 3px rgba(232,111,160,0.14), 0 6px 18px rgba(232,111,160,0.08);
}
div[data-testid="stTextInput"] > div {
    background: transparent !important; border: none !important; border-radius: 0 !important;
}
div[data-testid="stTextInput"] input {
    background: transparent !important; color: #3B2C24 !important;
    padding: 10px 4px !important; font-size: 15px !important;
}
div[data-testid="stTextInput"] input::placeholder { color: #B3A38F !important; }
div[data-testid="stTextInput"] > div > div {
    background: transparent !important;
}
div[data-baseweb="base-input"] {
    background: transparent !important;
}

.stButton button, .stFormSubmitButton button {
    background: linear-gradient(90deg, #F49CC4, #E86FA0);
    color: #FFFFFF !important; font-weight: 800; font-family: 'Space Grotesk', sans-serif;
    border: none; border-radius: 999px !important; padding: 12px 24px;
    box-shadow: 0 4px 14px rgba(232,111,160,0.3);
    transition: all 0.2s ease; font-size: 15px !important;
}
.stButton button:hover, .stFormSubmitButton button:hover {
    box-shadow: 0 6px 20px rgba(232,111,160,0.45);
    transform: translateY(-1px);
}

/* Sidebar timeline buttons */
section[data-testid="stSidebar"] .stButton button {
    background: transparent !important; color: #6B5A4A !important;
    box-shadow: none !important; border: none !important;
    text-align: left !important; font-weight: 400 !important; font-size: 13.5px !important;
    font-family: 'Inter', sans-serif !important; padding: 7px 8px 7px 4px !important;
    border-radius: 6px !important; border-left: 2px solid #F0DFC0 !important;
    margin-left: 4px;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: rgba(232,111,160,0.08) !important; color: #3B2C24 !important;
    border-left: 2px solid #E86FA0 !important;
}
section[data-testid="stSidebar"] .stButton button::first-letter { color: #E86FA0; }

.nx-archive-date {
    font-family: 'Space Grotesk', sans-serif; font-size: 11px; letter-spacing: 1.5px;
    color: #B3A38F; text-transform: uppercase; margin: 18px 0 4px 8px;
}

/* ---- Idle state ---- */
.nx-idle {
    text-align: center; padding: 60px 20px; border: 1px dashed #E8D4B0; border-radius: 18px;
    margin: 24px 0; background: #FFFDF6;
}
.nx-idle-ring {
    width: 56px; height: 56px; margin: 0 auto 18px auto; border-radius: 50%;
    border: 2px solid #F0DFC0; border-top: 2px solid #E86FA0;
    display: flex; align-items: center; justify-content: center;
    font-family: 'Space Grotesk', sans-serif; font-weight: 700; color: #E86FA0; font-size: 18px;
    animation: nx-spin-slow 6s linear infinite;
}
@keyframes nx-spin-slow { from { transform: rotate(0deg);} to { transform: rotate(360deg);} }
.nx-idle-title {
    font-family: 'Space Grotesk', sans-serif; font-weight: 800; font-size: 18px;
    letter-spacing: 1.5px; color: #3B2C24;
}
.nx-idle-sub { color: #8A7562; font-size: 13.5px; margin-top: 6px; }

/* ---- Journey rail ---- */
.nx-rail-wrap { padding: 18px 4px 6px 4px; margin: 18px 0 8px 0; }
.nx-rail { display: flex; align-items: flex-start; }
.nx-rail-step { display: flex; flex-direction: column; align-items: center; flex: 1; position: relative; }
.nx-rail-line {
    position: absolute; top: 16px; left: 50%; width: 100%; height: 2px; background: #F0DFC0; z-index: 1;
}
.nx-rail-line.done { background: linear-gradient(90deg, #F49CC4, #E86FA0); }
.nx-rail-circle {
    width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center;
    font-size: 13px; font-weight: 700; z-index: 2; border: 2px solid #F0DFC0; background: #FFFDF6; color: #B3A38F;
}
.nx-rail-circle.done { background: #E86FA0; border-color: #E86FA0; color: #FFFFFF; }
.nx-rail-circle.active {
    border-color: #E86FA0; color: #E86FA0; background: #FFFDF6;
    box-shadow: 0 0 0 5px rgba(232,111,160,0.14);
    animation: nx-pulse 1.1s infinite ease-in-out;
}
@keyframes nx-pulse { 0%,100% {opacity:1;} 50% {opacity:0.5;} }
.nx-rail-label { font-size: 11.5px; letter-spacing: 0.5px; text-transform: uppercase; margin-top: 8px; color: #B3A38F; font-weight: 600; }
.nx-rail-label.done, .nx-rail-label.active { color: #3B2C24; }
.nx-rail-detail { text-align: center; font-size: 13.5px; color: #8A7562; margin-top: 14px; min-height: 18px; }

/* ---- Intelligence Canvas ---- */
.nx-topic-card {
    background: #FFFDF6;
    border: 1px solid #F4B8D4; border-radius: 18px; padding: 28px 32px;
    max-width: 640px; margin: 26px auto 0 auto; text-align: center;
    box-shadow: 0 6px 24px rgba(232,111,160,0.1);
}
.nx-topic-eyebrow { font-size: 11.5px; letter-spacing: 1.5px; color: #E86FA0; text-transform: uppercase; margin-bottom: 8px; font-weight: 700; }
.nx-topic-text { font-family: 'Space Grotesk', sans-serif; font-size: 21px; font-weight: 700; color: #3B2C24; }

.nx-bus-line { width: 2px; height: 22px; margin: 0 auto; background: linear-gradient(180deg, #E86FA0, transparent); }
.nx-bus-horizontal { height: 1px; max-width: 900px; margin: 0 auto; background: linear-gradient(90deg, transparent, #E86FA055, transparent); }

.nx-source-card {
    background: #FFFDF6; border: 1px solid #F0DFC0; border-radius: 12px; padding: 16px 18px;
    position: relative; height: 100%;
}
.nx-source-card::before {
    content: ""; position: absolute; top: -16px; left: 50%; width: 1px; height: 16px;
    background: linear-gradient(180deg, #E86FA077, transparent);
}
.nx-source-cat {
    display: inline-block; font-size: 10.5px; letter-spacing: 0.5px; text-transform: uppercase; font-weight: 700;
    padding: 3px 9px; border-radius: 20px; background: #FBE4EF; color: #D9518B; margin-bottom: 9px;
}
.nx-source-title { font-size: 14px; font-weight: 600; color: #3B2C24; line-height: 1.45; margin-bottom: 7px; }
.nx-source-domain { font-size: 12px; color: #B3A38F; }

/* ---- Pills ---- */
.nx-pill {
    display: inline-block; font-size: 10.5px; font-weight: 700; letter-spacing: 0.5px;
    padding: 3px 10px; border-radius: 20px; margin-right: 6px; text-transform: uppercase;
}
.nx-pill-ai { background: #FBE4EF; color: #D9518B; }
.nx-pill-ready { background: #DFF2E8; color: #3F9C6E; }

/* ---- Content cards ---- */
.nx-content-card {
    background: #FFFDF6; border: 1px solid #F0DFC0; border-radius: 16px;
    padding: 22px 24px; margin-bottom: 14px;
}
.nx-content-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; flex-wrap: wrap; gap: 8px; }
.nx-content-platform-wrap { display: flex; align-items: center; gap: 10px; }
.nx-platform-icon {
    width: 28px; height: 28px; border-radius: 8px; display: flex; align-items: center; justify-content: center;
    font-size: 13px; font-weight: 700; font-family: 'Space Grotesk', sans-serif;
    background: linear-gradient(135deg, #F49CC4, #E86FA0); color: #fff;
}
.nx-content-platform { font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 14.5px; }
.nx-content-meta { font-size: 12px; color: #B3A38F; }
.nx-content-body { font-size: 15px; line-height: 1.7; color: #3B2C24; white-space: pre-wrap; }
.nx-content-hashtags { font-size: 13px; color: #D9518B; margin-top: 12px; }

/* ---- Completion banner ---- */
.nx-complete {
    background: #EAF7EF;
    border: 1px solid #B9E4C9; border-radius: 16px; padding: 20px 26px; margin: 20px 0;
    display: flex; align-items: center; gap: 18px;
}
.nx-complete-check {
    width: 44px; height: 44px; border-radius: 50%; background: #3F9C6E; color: #FFFFFF;
    display: flex; align-items: center; justify-content: center; font-size: 19px; font-weight: 700;
    flex-shrink: 0;
}
.nx-complete-title { font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 16px; letter-spacing: 0.5px; color: #3F9C6E; }
.nx-complete-detail { font-size: 13.5px; color: #6B8F7A; margin-top: 3px; }

/* ---- Terminal activity log ---- */
.nx-terminal {
    background: #FFFDF6; border: 1px solid #F0DFC0; border-radius: 12px; padding: 16px 20px;
    font-family: 'JetBrains Mono', monospace; font-size: 13px;
}
.nx-terminal-line { color: #6B8F7A; margin-bottom: 7px; }
.nx-terminal-time { color: #B3A38F; margin-right: 8px; }
.nx-terminal-prompt { color: #E86FA0; margin-right: 6px; font-weight: 700; }

[data-testid="stExpander"] { background: #FFFDF6 !important; border: 1px solid #F0DFC0 !important; border-radius: 10px !important; }
div[data-testid="stTextArea"] textarea {
    background: #FFFDF6 !important; color: #3B2C24 !important; border: 1px solid #F0DFC0 !important; border-radius: 10px !important;
    font-size: 14.5px !important;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# SESSION STATE
# ============================================================
defaults = {
    "activity_log": [],
    "active_report": None,
    "workflow_stage": -1,
    "edit_mode": {"linkedin": False, "instagram": False, "twitter": False},
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


def log_activity(msg: str):
    st.session_state.activity_log.insert(0, f"{datetime.now().strftime('%H:%M:%S')}||{msg}")
    st.session_state.activity_log = st.session_state.activity_log[:8]


# ============================================================
# RENDER HELPERS
# ============================================================
RAIL_STEPS = ["Research", "Analyze", "Select", "Generate", "Ready"]


def render_rail(stage_index: int, detail: str = ""):
    html = '<div class="nx-rail-wrap"><div class="nx-rail">'
    for i, step in enumerate(RAIL_STEPS):
        if stage_index > i or stage_index >= len(RAIL_STEPS):
            c_class, l_class, icon = "done", "done", "✓"
        elif stage_index == i:
            c_class, l_class, icon = "active", "active", "●"
        else:
            c_class, l_class, icon = "", "", str(i + 1)
        line = ""
        if i < len(RAIL_STEPS) - 1:
            line_done = "done" if stage_index > i or stage_index >= len(RAIL_STEPS) else ""
            line = f'<div class="nx-rail-line {line_done}"></div>'
        html += f"""
        <div class="nx-rail-step">{line}
            <div class="nx-rail-circle {c_class}">{icon}</div>
            <div class="nx-rail-label {l_class}">{step}</div>
        </div>"""
    html += f'</div><div class="nx-rail-detail">{detail}</div></div>'
    return html


def render_idle():
    return """
    <div class="nx-idle">
        <div class="nx-idle-ring">◆</div>
        <div class="nx-idle-title">NEXA IS READY</div>
        <div class="nx-idle-sub">Enter a topic above, or leave it blank and let NEXA discover what's trending.</div>
    </div>
    """


# ============================================================
# SIDEBAR — ARCHIVE TIMELINE
# ============================================================
with st.sidebar:
    st.markdown('<div class="nx-eyebrow">NEXA // Archive</div>', unsafe_allow_html=True)

    if "confirm_clear_history" not in st.session_state:
        st.session_state.confirm_clear_history = False

    report_files = sorted(glob.glob("daily_reports/*.json"), reverse=True)
    if not report_files:
        st.caption("No reports generated yet.")
    else:
        grouped = {}
        for fpath in report_files:
            mtime = datetime.fromtimestamp(os.path.getmtime(fpath))
            d = mtime.date()
            label = "TODAY" if d == date.today() else ("YESTERDAY" if d == date.today() - timedelta(days=1) else d.strftime("%B %d").upper())
            grouped.setdefault(label, []).append((fpath, mtime))

        for label, items in grouped.items():
            st.markdown(f'<div class="nx-archive-date">{label}</div>', unsafe_allow_html=True)
            for fpath, mtime in items:
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    topic = data.get("topic", "Untitled")
                    short = topic if len(topic) <= 34 else topic[:31] + "..."
                    if st.button(f"● {mtime.strftime('%H:%M')}  {short}", key=fpath, use_container_width=True):
                        data["_path"] = fpath
                        st.session_state.active_report = data
                        st.session_state.workflow_stage = 5
                        st.session_state.edit_mode = {"linkedin": False, "instagram": False, "twitter": False}
                except (json.JSONDecodeError, KeyError):
                    continue

        st.markdown("<br>", unsafe_allow_html=True)
        if not st.session_state.confirm_clear_history:
            if st.button("🗑 Clear History", use_container_width=True):
                st.session_state.confirm_clear_history = True
                st.rerun()
        else:
            st.warning("Delete all saved daily reports? This can't be undone.")
            cc1, cc2 = st.columns(2)
            with cc1:
                if st.button("Cancel", use_container_width=True, key="cancel_clear"):
                    st.session_state.confirm_clear_history = False
                    st.rerun()
            with cc2:
                if st.button("Delete", use_container_width=True, type="primary", key="confirm_clear"):
                    for f in report_files:
                        os.remove(f)
                    st.session_state.active_report = None
                    st.session_state.confirm_clear_history = False
                    st.rerun()

# ============================================================
# HEADER
# ============================================================
st.markdown('<div style="font-size:10.5px; letter-spacing:3px; color:#8E98AA; text-transform:uppercase;">Nexariza AI · Agentic Systems</div>', unsafe_allow_html=True)
st.markdown('<div class="nx-title">NEXA // Content Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="nx-sub">Autonomous content intelligence for Nexariza AI</div>', unsafe_allow_html=True)

# ============================================================
# COMMAND CAPSULE
# ============================================================
with st.form(key="gen_form", clear_on_submit=True):
    c1, c2 = st.columns([5, 1.4])
    with c1:
        topic_input = st.text_input(
            "topic", placeholder="✦ What should NEXA explore today? Enter a topic or leave blank for automatic discovery…",
            label_visibility="collapsed"
        )
    with c2:
        generate_clicked = st.form_submit_button("Generate ✦", use_container_width=True)
rail_slot = st.empty()
canvas_slot = st.empty()

if not st.session_state.active_report:
    rail_slot.markdown(render_rail(-1), unsafe_allow_html=True)
    canvas_slot.markdown(render_idle(), unsafe_allow_html=True)
else:
    rail_slot.markdown(render_rail(st.session_state.workflow_stage), unsafe_allow_html=True)

# ============================================================
# GENERATION PIPELINE
# ============================================================
if generate_clicked:
    st.session_state.activity_log = []
    st.session_state.edit_mode = {"linkedin": False, "instagram": False, "twitter": False}

    rail_slot.markdown(render_rail(0, "Searching AI/tech sources across the web…"), unsafe_allow_html=True)
    research = research_topic(topic_override=topic_input if topic_input else None)
    log_activity(f"{len(research['sources'])} sources retrieved")
    time.sleep(0.4)

    rail_slot.markdown(render_rail(1, "Analyzing topic relevance across sources…"), unsafe_allow_html=True)
    time.sleep(0.5)
    log_activity("Relevance analysis complete")

    rail_slot.markdown(render_rail(2, f'Topic selected: "{research["selected_topic"]}"'), unsafe_allow_html=True)
    log_activity(f"Topic selected: {research['selected_topic']}")
    time.sleep(0.5)

    rail_slot.markdown(render_rail(3, "Writing LinkedIn post…"), unsafe_allow_html=True)
    linkedin = generate_linkedin_post(research["selected_topic"])
    log_activity("LinkedIn post generated")

    rail_slot.markdown(render_rail(3, "Writing Instagram caption…"), unsafe_allow_html=True)
    instagram = generate_instagram_caption(research["selected_topic"])
    log_activity("Instagram caption generated")

    rail_slot.markdown(render_rail(3, "Writing X / Twitter thread…"), unsafe_allow_html=True)
    twitter = generate_twitter_thread(research["selected_topic"])
    log_activity("X/Twitter thread generated")

    report = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "topic": research["selected_topic"],
        "sources": research["sources"],
        "linkedin_post": linkedin,
        "instagram": instagram,
        "twitter_thread": twitter,
    }
    path = save_daily_report(report)
    report["_path"] = path
    log_activity("Daily report saved")

    st.session_state.active_report = report
    st.session_state.workflow_stage = 5
    rail_slot.markdown(render_rail(5), unsafe_allow_html=True)
    canvas_slot.empty()

# ============================================================
# INTELLIGENCE CANVAS + OUTPUT
# ============================================================
active = st.session_state.active_report
if active:
    sources = active.get("sources", [])

    # --- Completion banner ---
    st.markdown(f"""
    <div class="nx-complete">
        <div class="nx-complete-check">✓</div>
        <div>
            <div class="nx-complete-title">CONTENT READY</div>
            <div class="nx-complete-detail">{len(sources)} sources analyzed · 3 platforms generated · report saved</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- Intelligence Canvas ---
    st.markdown('<div class="nx-eyebrow">NEXA // Research</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div class="nx-topic-card">
        <div class="nx-topic-eyebrow">Selected Topic</div>
        <div class="nx-topic-text">{active['topic']}</div>
    </div>
    <div class="nx-bus-line"></div>
    """, unsafe_allow_html=True)

    if sources:
        st.markdown('<div class="nx-bus-horizontal"></div>', unsafe_allow_html=True)
        st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
        cols = st.columns(min(4, len(sources)))
        for i, src in enumerate(sources[:8]):
            with cols[i % len(cols)]:
                title = src.get("title", "Untitled")
                short_title = title if len(title) <= 70 else title[:67] + "..."
                st.markdown(f"""
                <div class="nx-source-card">
                    <div class="nx-source-cat">{src.get('category', 'source')}</div>
                    <div class="nx-source-title">{short_title}</div>
                    <div class="nx-source-domain">{src.get('domain', '')}</div>
                    <a href="{src.get('url', '#')}" target="_blank" style="font-size:11px; color:#F36B6B; text-decoration:none;">View Source ↗</a>
                </div>
                """, unsafe_allow_html=True)

 

    # --- Output cards ---
    st.markdown('<div class="nx-eyebrow">NEXA // Output</div>', unsafe_allow_html=True)

    def platform_card(platform_key, icon, platform_name, body_text, meta_extra="", hashtags=None):
        hashtags_html = f'<div class="nx-content-hashtags">{hashtags}</div>' if hashtags else ""
        card_html = (
            '<div class="nx-content-card">'
            '<div class="nx-content-header">'
            '<div class="nx-content-platform-wrap">'
            f'<div class="nx-platform-icon">{icon}</div>'
            f'<div class="nx-content-platform">{platform_name}</div>'
            '</div>'
            f'<div class="nx-content-meta"><span class="nx-pill nx-pill-ai">AI Generated</span><span class="nx-pill nx-pill-ready">Ready</span> {meta_extra}</div>'
            '</div>'
            f'<div class="nx-content-body">{body_text}</div>'
            f'{hashtags_html}'
            '</div>'
        )
        st.markdown(card_html, unsafe_allow_html=True)

        col_copy, col_edit, col_regen = st.columns([1, 1, 1])
        edit_on = st.session_state.edit_mode[platform_key]

        with col_copy:
            with st.popover("📋 Copy", use_container_width=True):
                st.code(body_text if not hashtags else f"{body_text}\n\n{hashtags}", language=None)
        with col_edit:
            if st.button("✎ Edit" if not edit_on else "✓ Done", key=f"edit_btn_{platform_key}", use_container_width=True):
                st.session_state.edit_mode[platform_key] = not edit_on
                st.rerun()
        with col_regen:
            if st.button("↻ Regenerate", key=f"regen_btn_{platform_key}", use_container_width=True):
                topic = st.session_state.active_report["topic"]
                if platform_key == "linkedin":
                    st.session_state.active_report["linkedin_post"] = generate_linkedin_post(topic)
                elif platform_key == "instagram":
                    st.session_state.active_report["instagram"] = generate_instagram_caption(topic)
                elif platform_key == "twitter":
                    st.session_state.active_report["twitter_thread"] = generate_twitter_thread(topic)
                if "_path" in st.session_state.active_report:
                    save_daily_report({k: v for k, v in st.session_state.active_report.items() if not k.startswith("_")})
                log_activity(f"{platform_name} regenerated")
                st.rerun()

        if edit_on:
            new_val = st.text_area(f"Edit {platform_name}", value=body_text, key=f"ta_{platform_key}", height=140, label_visibility="collapsed")
            if platform_key == "linkedin":
                st.session_state.active_report["linkedin_post"] = new_val
            elif platform_key == "instagram":
                st.session_state.active_report["instagram"]["caption"] = new_val

    linkedin_words = len(active["linkedin_post"].split())
    platform_card("linkedin", "in", "LinkedIn", active["linkedin_post"], meta_extra=f"{linkedin_words} words")

    ig = active["instagram"]
    platform_card("instagram", "ig", "Instagram", ig["caption"], hashtags=ig["hashtags"])

    tw = active["twitter_thread"]
    tw_text = "\n".join(tw)
    platform_card("twitter", "X", "X / Twitter Thread", tw_text, meta_extra=f"{len(tw)} tweets")

st.markdown('<div style="color:#5C6478; font-size:11.5px; margin-top:34px; letter-spacing:1px;">BUILT BY AREEBA ZAKA — NEXARIZA AI AGENTIC AI INTERNSHIP</div>', unsafe_allow_html=True)