"""
Nexariza AI Internship 
ReAct Agent — Styled Demo UI with History + Sources + Mascot
"""

import ast
import streamlit as st
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import ToolMessage
from langgraph.prebuilt import create_react_agent

load_dotenv()
import json
import os

HISTORY_FILE = "chat_history.json"

def load_history_from_disk():
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
        for entry in raw:
            entry["timestamp"] = datetime.fromisoformat(entry["timestamp"])
        return raw
    except (json.JSONDecodeError, KeyError, ValueError):
        return []

def save_history_to_disk(history):
    serializable = []
    for entry in history:
        e = dict(entry)
        e["timestamp"] = e["timestamp"].isoformat()
        serializable.append(e)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(serializable, f, ensure_ascii=False, indent=2)

st.set_page_config(page_title="Nexariza AI — ReAct Agent", page_icon="◆", layout="wide")

# ---------- Custom styling (warm cream / brown palette) ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;500&display=swap');

html, body, [class*="css"]  { font-family: 'Inter', sans-serif; }

.stApp {
    background-color: #F5E4CA;
    background-image:
        radial-gradient(circle at 8px 8px, rgba(111,96,78,0.10) 1.5px, transparent 1.5px),
        linear-gradient(135deg, rgba(111,96,78,0.04) 1px, transparent 1px),
        linear-gradient(45deg, rgba(111,96,78,0.04) 1px, transparent 1px);
    background-size: 34px 34px, 68px 68px, 68px 68px;
    color: #332821;
}

section[data-testid="stSidebar"] {
    background: #FCF4E4;
    border-right: 1px solid #E7D7BD;
}

.nx-eyebrow {
    font-family: 'Space Grotesk', sans-serif;
    letter-spacing: 3px; font-size: 12px; color: #756A5E;
    text-transform: uppercase; margin-bottom: 4px;
}
.nx-title {
    font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 38px;
    background: linear-gradient(90deg, #6F604E 0%, #3B2C24 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 2px;
}
.nx-sub { color: #756A5E; font-size: 14px; margin-bottom: 28px; }

/* ---- Fix: override BaseWeb's wrapper div, which is where the default red focus ring lives ---- */
div[data-testid="stTextInput"] > div {
    background-color: #F5E4CA !important;
    border: 1px solid #6F604E !important;
    border-radius: 10px !important;
    box-shadow: none !important;
}
div[data-testid="stTextInput"] > div:focus-within {
    border: 1px solid #3B2C24 !important;
    box-shadow: 0 0 0 3px rgba(111,96,78,0.18) !important;
}
div[data-testid="stTextInput"] input {
    background-color: transparent !important;
    border: none !important;
    color: #332821 !important;
    padding: 12px 14px !important;
    box-shadow: none !important;
}
div[data-testid="stTextInput"] input:focus {
    outline: none !important;
    box-shadow: none !important;
}
div[data-testid="stTextInput"] input::placeholder { color: #A99B87 !important; }

.stButton button, .stFormSubmitButton button {
    background: #3B2C24;
    color: #FCF4E4 !important;
    font-weight: 700; font-family: 'Space Grotesk', sans-serif;
    border: none; border-radius: 10px; padding: 10px 24px;
    box-shadow: 0 0 16px rgba(59,44,36,0.35), 0 0 30px rgba(111,96,78,0.2);
    transition: all 0.25s ease;
}
.stButton button:hover, .stFormSubmitButton button:hover {
    box-shadow: 0 0 26px rgba(59,44,36,0.5), 0 0 42px rgba(111,96,78,0.35);
    transform: translateY(-1px);
    background: #4a382e;
}

.nx-answer-card {
    background: #FCF4E4; border: 1px solid #E7D7BD; border-left: 3px solid #6F604E;
    border-radius: 12px; padding: 22px 24px; margin-top: 20px;
    animation: nx-fade-in 0.5s ease;
    color: #332821;
}
@keyframes nx-fade-in { from { opacity: 0; transform: translateY(6px);} to {opacity: 1; transform: translateY(0);} }
.nx-answer-label {
    font-family: 'Space Grotesk', sans-serif; font-size: 12px; letter-spacing: 2px;
    color: #6F604E; text-transform: uppercase; margin-bottom: 10px;
}

.nx-thinking { display: flex; align-items: center; gap: 10px; color: #756A5E; font-size: 14px; margin-top: 16px; }
.nx-dot { width: 8px; height: 8px; border-radius: 50%; background: #6F604E; animation: nx-pulse 1.1s infinite ease-in-out; }
.nx-dot:nth-child(2) { animation-delay: 0.2s; background: #E5C9A2; }
.nx-dot:nth-child(3) { animation-delay: 0.4s; background: #3B2C24; }
@keyframes nx-pulse { 0%, 80%, 100% { opacity: 0.3; transform: scale(0.8);} 40% { opacity: 1; transform: scale(1.15);} }

.nx-sources-label {
    font-family: 'Space Grotesk', sans-serif; font-size: 12px; letter-spacing: 2px;
    color: #6F604E; text-transform: uppercase; margin-top: 18px; margin-bottom: 8px;
}

.nx-history-date {
    font-family: 'Space Grotesk', sans-serif; font-size: 11px; letter-spacing: 2px;
    color: #756A5E; text-transform: uppercase; margin: 18px 0 6px 4px;
    border-bottom: 1px solid #E7D7BD; padding-bottom: 6px;
}

section[data-testid="stSidebar"] .stButton button {
    background: #FCF4E4 !important;
    color: #332821 !important;
    box-shadow: none !important;
    border: 1px solid #E7D7BD !important;
    text-align: left !important;
    font-family: 'Inter', sans-serif !important;
    font-weight: 400 !important;
    padding: 8px 10px !important;
}
section[data-testid="stSidebar"] .stButton button:hover {
    background: #EAD4B4 !important;
    transform: none !important;
    box-shadow: none !important;
}

.nx-footer { color: #A99B87; font-size: 12px; margin-top: 40px; letter-spacing: 1px; }

[data-testid="stExpander"] {
    background: #F5E4CA !important;
    border: 1px solid #E7D7BD !important;
    border-radius: 8px !important;
}

/* ---------- Robot mascot ---------- */
.nx-mascot-wrap {
    position: fixed;
    bottom: 22px;
    right: 26px;
    z-index: 999;
    display: flex;
    flex-direction: column;
    align-items: center;
    pointer-events: none;
}
.nx-mascot {
    width: 74px;
    animation: nx-bob 2.6s ease-in-out infinite;
    transform-origin: bottom center;
}
.nx-mascot.thinking { animation: nx-bob-fast 0.7s ease-in-out infinite; }
@keyframes nx-bob {
    0%, 100% { transform: translateY(0) rotate(0deg); }
    50% { transform: translateY(-8px) rotate(-2deg); }
}
@keyframes nx-bob-fast {
    0%, 100% { transform: translateY(0) rotate(0deg); }
    50% { transform: translateY(-5px) rotate(3deg); }
}
.nx-arm-r {
    transform-origin: 60px 58px;
    animation: nx-wave 2.6s ease-in-out infinite;
}
@keyframes nx-wave {
    0%, 60%, 100% { transform: rotate(0deg); }
    75% { transform: rotate(-22deg); }
    85% { transform: rotate(-8deg); }
}
.nx-eye { animation: nx-blink 4s infinite; }
.nx-mascot.thinking .nx-eye { animation: nx-blink-fast 0.5s infinite; }
@keyframes nx-blink {
    0%, 92%, 100% { transform: scaleY(1); }
    96% { transform: scaleY(0.1); }
}
@keyframes nx-blink-fast {
    0%, 100% { transform: scaleY(1); }
    50% { transform: scaleY(0.3); }
}
.nx-bubble {
    background: #3B2C24;
    color: #FCF4E4;
    font-size: 11px;
    padding: 4px 10px;
    border-radius: 10px;
    margin-bottom: 6px;
    font-family: 'Space Grotesk', sans-serif;
    opacity: 0;
    animation: nx-bubble-fade 3.5s ease-in-out infinite;
}
.nx-mascot-wrap.thinking .nx-bubble { animation: nx-bubble-fade 1s ease-in-out infinite; opacity: 1; }
@keyframes nx-bubble-fade {
    0%, 15% { opacity: 0; transform: translateY(4px); }
    25%, 75% { opacity: 1; transform: translateY(0); }
    90%, 100% { opacity: 0; transform: translateY(4px); }
}
</style>
""", unsafe_allow_html=True)


def robot_svg(eye_color="#3B2C24"):
    return f"""
    <svg class="nx-mascot" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="50" cy="92" rx="20" ry="4" fill="#3B2C24" opacity="0.12"/>
        <rect x="30" y="42" width="40" height="34" rx="12" fill="#FCF4E4" stroke="#6F604E" stroke-width="2.5"/>
        <rect x="38" y="14" width="24" height="28" rx="10" fill="#FCF4E4" stroke="#6F604E" stroke-width="2.5"/>
        <circle cx="50" cy="8" r="3" fill="#E5C9A2" stroke="#6F604E" stroke-width="2"/>
        <line x1="50" y1="11" x2="50" y2="14" stroke="#6F604E" stroke-width="2"/>
        <g class="nx-eye">
            <circle cx="45" cy="27" r="3" fill="{eye_color}"/>
            <circle cx="57" cy="27" r="3" fill="{eye_color}"/>
        </g>
        <path d="M45 34 Q50 37 55 34" stroke="{eye_color}" stroke-width="2" fill="none" stroke-linecap="round"/>
        <rect x="14" y="48" width="10" height="20" rx="5" fill="#E5C9A2" stroke="#6F604E" stroke-width="2"/>
        <g class="nx-arm-r">
            <rect x="76" y="48" width="10" height="20" rx="5" fill="#E5C9A2" stroke="#6F604E" stroke-width="2"/>
        </g>
        <rect x="36" y="78" width="10" height="14" rx="4" fill="#6F604E"/>
        <rect x="54" y="78" width="10" height="14" rx="4" fill="#6F604E"/>
    </svg>
    """


# ---------- Session state ----------
if "history" not in st.session_state:
    st.session_state.history = load_history_from_disk()
if "confirm_clear" not in st.session_state:
    st.session_state.confirm_clear = False
if "active_answer" not in st.session_state:
    st.session_state.active_answer = None


# ---------- Agent setup ----------
@st.cache_resource
def load_agent():
    llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)
    search_tool = TavilySearchResults(max_results=3)
    return create_react_agent(llm, [search_tool])

agent = load_agent()


def extract_sources(messages):
    sources = []
    for msg in messages:
        if isinstance(msg, ToolMessage):
            content = msg.content
            try:
                parsed = ast.literal_eval(content) if isinstance(content, str) else content
                if isinstance(parsed, list):
                    for item in parsed:
                        if isinstance(item, dict) and "url" in item:
                            sources.append({
                                "title": item.get("title", item.get("url")),
                                "url": item.get("url"),
                                "snippet": item.get("content", "")[:200]
                            })
            except (ValueError, SyntaxError):
                continue
    return sources


def date_label(ts: datetime) -> str:
    d = ts.date()
    today = date.today()
    if d == today:
        return "TODAY"
    if d == today - timedelta(days=1):
        return "YESTERDAY"
    return d.strftime("%B %d").upper()


def run_agent(q: str):
    result = agent.invoke({"messages": [("user", q)]})
    answer = result["messages"][-1].content
    sources = extract_sources(result["messages"])

    entry = {
        "id": len(st.session_state.history),
        "question": q,
        "answer": answer,
        "sources": sources,
        "timestamp": datetime.now(),
    }
    st.session_state.history.append(entry)
    st.session_state.active_answer = entry
    save_history_to_disk(st.session_state.history)

# ---------- Sidebar: history ----------
with st.sidebar:
    st.markdown('<div class="nx-eyebrow">Nexariza AI</div>', unsafe_allow_html=True)
    st.markdown('<div style="font-family:Space Grotesk; font-weight:700; font-size:18px; color:#332821; margin-bottom:16px;">History</div>', unsafe_allow_html=True)

    if not st.session_state.history:
        st.caption("No questions yet.")
    else:
        grouped = {}
        for entry in reversed(st.session_state.history):
            label = date_label(entry["timestamp"])
            grouped.setdefault(label, []).append(entry)

        for label, entries in grouped.items():
            st.markdown(f'<div class="nx-history-date">{label}</div>', unsafe_allow_html=True)
            for entry in entries:
                short_q = entry["question"] if len(entry["question"]) <= 40 else entry["question"][:37] + "..."
                if st.button(short_q, key=f"hist_{entry['id']}", use_container_width=True):
                    st.session_state.active_answer = entry

        st.markdown("<br>", unsafe_allow_html=True)

        if not st.session_state.confirm_clear:
            if st.button("🗑 Clear History", use_container_width=True):
                st.session_state.confirm_clear = True
                st.rerun()
        else:
            st.warning("Delete all history? This can't be undone.")
            c1, c2 = st.columns(2)
            with c1:
                if st.button("Cancel", use_container_width=True):
                    st.session_state.confirm_clear = False
                    st.rerun()
            with c2:
                if st.button("Delete", use_container_width=True, type="primary"):
                    st.session_state.history = []
                    st.session_state.active_answer = None
                    st.session_state.confirm_clear = False
                    st.rerun()
                    if st.button("Delete", use_container_width=True, type="primary"):
                     st.session_state.history = []
                    st.session_state.active_answer = None
                    st.session_state.confirm_clear = False
                    save_history_to_disk([])   # add this line
                    st.rerun()

# ---------- Header ----------
st.markdown('<div class="nx-eyebrow">Nexariza AI · Agentic Systems</div>', unsafe_allow_html=True)
st.markdown('<div class="nx-title">ReAct Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="nx-sub">Web-search-powered reasoning agent, built on Groq + Tavily</div>', unsafe_allow_html=True)

# ---------- Input (form so Enter and button both submit, clears after submit) ----------
with st.form(key="ask_form", clear_on_submit=True):
    question = st.text_input(
        "Ask a question",
        placeholder="Ask anything...",
        label_visibility="collapsed"
    )
    col1, col2 = st.columns([1, 5])
    with col1:
        ask_clicked = st.form_submit_button("Ask Agent →")

# ---------- Mascot placeholder (always present, swaps to "thinking" state) ----------
mascot_slot = st.empty()
mascot_slot.markdown(f'<div class="nx-mascot-wrap">{robot_svg()}</div>', unsafe_allow_html=True)

if ask_clicked and question:
    mascot_slot.markdown(f"""
    <div class="nx-mascot-wrap thinking">
        <div class="nx-bubble">thinking...</div>
        {robot_svg()}
    </div>
    """, unsafe_allow_html=True)

    answer_placeholder = st.empty()
    answer_placeholder.markdown("""
    <div class="nx-thinking">
        <div class="nx-dot"></div><div class="nx-dot"></div><div class="nx-dot"></div>
        Agent is searching and reasoning...
    </div>
    """, unsafe_allow_html=True)

    run_agent(question)
    answer_placeholder.empty()

    mascot_slot.markdown(f'<div class="nx-mascot-wrap">{robot_svg()}</div>', unsafe_allow_html=True)

# ---------- Display active answer ----------
active = st.session_state.active_answer
if active:
    st.markdown(f"""
    <div class="nx-answer-card">
        <div class="nx-answer-label">Answer</div>
        {active['answer']}
    </div>
    """, unsafe_allow_html=True)

    if active["sources"]:
        st.markdown(f'<div class="nx-sources-label">🔗 {len(active["sources"])} sources found</div>', unsafe_allow_html=True)
        for src in active["sources"]:
            with st.expander(src["title"]):
                st.write(src["snippet"])
                st.markdown(f"[Visit source]({src['url']})")

st.markdown('<div class="nx-footer">BUILT BY Areeba Zaka, NEXARIZA AI AGENTIC AI </div>', unsafe_allow_html=True)