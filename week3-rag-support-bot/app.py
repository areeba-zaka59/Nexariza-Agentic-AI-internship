"""
Nexariza AI Internship — Week 3
Nexariza AI Support — Lavender & Sage theme with inline mascot avatars
"""

import os
import re
import json
import glob
import uuid
from datetime import datetime, date, timedelta
import streamlit as st

from rag_pipeline import (
    build_vector_store,
    load_vector_store,
    answer_question,
    generate_followups,
    ESCALATION_CONTACT,
    VECTOR_DB_DIR,
)

st.set_page_config(page_title="Nexariza AI Support", page_icon="✦", layout="wide")

SESSIONS_DIR = "chat_sessions"
os.makedirs(SESSIONS_DIR, exist_ok=True)
FEEDBACK_FILE = "feedback_log.json"

T = {
    "name": "Lavender & Sage",
    "page_bg": "#F6F4FB", "header_bg": "#7C8B99", "header_text": "#FFFFFF",
    "sidebar_bg": "#2E2A3D", "sidebar_text": "#EDE7F6",
    "card_bg": "#FFFFFF", "border": "#E3DEF2",
    "bot_bubble": "#D9CDF0", "bot_text": "#3A2E5C",
    "user_bubble": "#8FD9A0", "user_text": "#1C3B24",
    "accent": "#8B78B8", "text": "#2B2438",
}


def render_markdown_lite(text: str) -> str:
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = text.replace("\n", "<br>")
    return text


def mascot_svg(accent: str, size: int = 44, thinking: bool = False):
    """Cute robot with head + body, used as an inline avatar next to bot messages."""
    cls = "nx5-avatar thinking" if thinking else "nx5-avatar"
    return f"""
    <svg class="{cls}" width="{size}" height="{size}" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
        <rect x="30" y="46" width="40" height="34" rx="12" fill="#FFFFFF" stroke="{accent}" stroke-width="3"/>
        <circle cx="50" cy="26" r="20" fill="#FFFFFF" stroke="{accent}" stroke-width="3"/>
        <circle cx="50" cy="8" r="3" fill="{accent}"/>
        <line x1="50" y1="11" x2="50" y2="16" stroke="{accent}" stroke-width="2.5"/>
        <circle cx="43" cy="26" r="4" fill="{accent}"/>
        <circle cx="57" cy="26" r="4" fill="{accent}"/>
        <path d="M43 34 Q50 39 57 34" stroke="{accent}" stroke-width="2.5" fill="none" stroke-linecap="round"/>
        <rect x="14" y="52" width="10" height="18" rx="5" fill="{accent}" opacity="0.75"/>
        <rect x="76" y="52" width="10" height="18" rx="5" fill="{accent}" opacity="0.75"/>
    </svg>
    """


# ============================================================
# STYLING
# ============================================================
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@600;700;800&family=Inter:wght@400;500;600&display=swap');
html, body, [class*="css"] {{ font-family: 'Inter', sans-serif; }}

.stApp {{ background: {T['page_bg']}; color: {T['text']}; }}
section[data-testid="stSidebar"] {{ background: {T['sidebar_bg']}; }}
section[data-testid="stSidebar"] * {{ color: {T['sidebar_text']}; }}

.nx5-header {{ background: {T['header_bg']}; color: {T['header_text']}; border-radius: 16px; padding: 16px 22px; margin-bottom: 18px; }}
.nx5-header-title {{ font-family: 'Space Grotesk', sans-serif; font-weight: 700; font-size: 16px; }}
.nx5-header-sub {{ font-size: 12px; opacity: 0.85; margin-top: 1px; }}

.nx5-brand {{ display:flex; align-items:center; gap:10px; margin-bottom:22px; }}
.nx5-brand-icon {{ width:34px; height:34px; border-radius:9px; background:{T['accent']}; display:flex; align-items:center; justify-content:center; font-weight:800; color:#fff; font-size:15px; }}
.nx5-brand-name {{ font-family:'Space Grotesk', sans-serif; font-weight:800; font-size:19px; color: #FFFFFF; letter-spacing: 0.3px; }}

.stButton button {{
    background: {T['card_bg']} !important; color: {T['accent']} !important;
    border: 1px solid {T['border']} !important; border-radius: 18px !important;
    font-size: 12.5px !important; font-weight: 500 !important; padding: 6px 12px !important; box-shadow: none !important;
}}
section[data-testid="stSidebar"] .stButton button {{ background: {T['accent']} !important; color: #FFFFFF !important; font-weight: 700 !important; border: none !important; }}
div[data-testid="stDownloadButton"] button {{
    background: {T['card_bg']} !important; color: {T['accent']} !important; border: 1px solid {T['border']} !important;
    border-radius: 18px !important; box-shadow: none !important; font-size: 12px !important;
}}

.nx5-msg-row {{ display: flex; align-items: flex-end; gap: 8px; margin-bottom: 4px; }}
.nx5-msg-row.user {{ justify-content: flex-end; }}
.nx5-msg-row.bot {{ justify-content: flex-start; }}
.nx5-bubble {{ max-width: 62%; padding: 11px 15px; border-radius: 15px; font-size: 14px; line-height: 1.55; }}
.nx5-bubble.user {{ background: {T['user_bubble']}; color: {T['user_text']}; border-bottom-right-radius: 4px; }}
.nx5-bubble.bot {{ background: {T['bot_bubble']}; color: {T['bot_text']}; border-bottom-left-radius: 4px; }}
.nx5-timestamp {{ font-size: 10px; opacity: 0.55; margin: 2px 4px 14px 52px; }}

.nx5-avatar {{ flex-shrink: 0; }}
.nx5-avatar.latest {{ animation: nx5-bounce 1.4s ease-in-out infinite; }}
.nx5-avatar.thinking {{ animation: nx5-bounce-fast 0.6s ease-in-out infinite; }}
@keyframes nx5-bounce {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-6px); }} }}
@keyframes nx5-bounce-fast {{ 0%,100% {{ transform: translateY(0); }} 50% {{ transform: translateY(-8px); }} }}

.nx5-escalate {{ background: {T['card_bg']}; border: 1px solid {T['accent']}55; border-radius: 12px; padding: 12px 16px; margin: 4px 0 14px 52px; max-width: 62%; font-size: 12.5px; }}
.nx5-escalate a {{ display:inline-block; font-size:11.5px; font-weight:600; color:#fff; background:{T['accent']}; padding:5px 10px; border-radius:8px; text-decoration:none; margin-right:6px; margin-top:6px; }}
.nx5-followup-label {{ font-size: 11px; opacity: 0.65; margin: 6px 0 6px 52px; }}
.nx5-typing-row {{ display:flex; align-items:center; gap:10px; margin: 6px 0 16px 0; }}
.nx5-typing-text {{ font-size: 12.5px; opacity: 0.6; font-style: italic; }}

div[data-testid="stChatInput"] {{ border-radius: 999px !important; border: 1px solid {T['accent']} !important; background: #1F2330 !important; }}
div[data-testid="stChatInput"] textarea {{ background: transparent !important; color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important; }}
div[data-testid="stChatInput"] textarea::placeholder {{ color: #B8B8C4 !important; }}
</style>
""", unsafe_allow_html=True)


# ============================================================
# BACKEND HELPERS
# ============================================================
@st.cache_resource
def get_vector_store():
    if not os.path.exists(VECTOR_DB_DIR):
        with st.spinner("Setting up the knowledge base for the first time..."):
            return build_vector_store()
    return load_vector_store()


vectordb = get_vector_store()

SUGGESTIONS = [
    "What services do you offer?",
    "What's your pricing?",
    "Who founded Nexariza AI?",
    "How can I contact your team?",
]


def session_path(session_id):
    return f"{SESSIONS_DIR}/{session_id}.json"


def save_session(session_id, messages, title=None):
    data = {
        "id": session_id,
        "title": title or (messages[0]["content"][:40] if messages else "New conversation"),
        "updated_at": datetime.now().isoformat(),
        "messages": messages,
    }
    with open(session_path(session_id), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_all_sessions():
    sessions = []
    for fpath in sorted(glob.glob(f"{SESSIONS_DIR}/*.json"), key=os.path.getmtime, reverse=True):
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                sessions.append(json.load(f))
        except (json.JSONDecodeError, KeyError):
            continue
    return sessions


def date_label(ts):
    d = ts.date()
    today = date.today()
    if d == today:
        return "TODAY"
    if d == today - timedelta(days=1):
        return "YESTERDAY"
    return d.strftime("%B %d").upper()


def save_feedback(question, answer, vote):
    entries = []
    if os.path.exists(FEEDBACK_FILE):
        try:
            with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
                entries = json.load(f)
        except (json.JSONDecodeError, ValueError):
            entries = []
    entries.append({"question": question, "answer": answer, "vote": vote, "timestamp": datetime.now().isoformat()})
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


# ============================================================
# SESSION STATE
# ============================================================
if "active_session_id" not in st.session_state:
    st.session_state.active_session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []

chat_end_slot = None  # assigned later, used by handle_question


def start_new_chat():
    st.session_state.active_session_id = str(uuid.uuid4())
    st.session_state.messages = []


def handle_question(question):
    st.session_state.messages.append({
        "role": "user", "content": question, "sources": [], "escalate": False,
        "time": datetime.now().strftime("%H:%M"),
    })
    if chat_end_slot is not None:
        typing_html = (
            '<div class="nx5-typing-row">'
            + mascot_svg(T['accent'], size=40, thinking=True)
            + '<div class="nx5-typing-text">Nexariza AI is typing...</div>'
            + '</div>'
        )
        chat_end_slot.markdown(typing_html, unsafe_allow_html=True)

    result = answer_question(vectordb, question)
    followups = generate_followups(question, result["answer"])

    st.session_state.messages.append({
        "role": "bot", "content": result["answer"], "sources": result["sources"],
        "escalate": result["escalate"], "time": datetime.now().strftime("%H:%M"),
        "followups": followups, "feedback": None,
    })
    save_session(st.session_state.active_session_id, st.session_state.messages)


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown(f"""
    <div class="nx5-brand">
        <div class="nx5-brand-icon">N</div>
        <div class="nx5-brand-name">Nexariza AI Support</div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("＋ New Chat", use_container_width=True):
        start_new_chat()
        st.rerun()

    st.markdown('<div style="font-size:10.5px; letter-spacing:1.5px; opacity:0.6; margin:20px 0 8px 2px; text-transform:uppercase;">Recent Conversations</div>', unsafe_allow_html=True)

    sessions = load_all_sessions()
    if "confirm_clear" not in st.session_state:
        st.session_state.confirm_clear = False

    if not sessions:
        st.caption("No past conversations yet.")
    else:
        grouped = {}
        for s in sessions:
            if not s.get("messages"):
                continue
            ts = datetime.fromisoformat(s["updated_at"])
            grouped.setdefault(date_label(ts), []).append((s, ts))
        for label, items in grouped.items():
            st.markdown(f'<div style="font-size:10px; opacity:0.5; margin:10px 0 4px 2px;">{label}</div>', unsafe_allow_html=True)
            for s, ts in items:
                title = s["title"] if len(s["title"]) <= 30 else s["title"][:27] + "..."
                if st.button(f"💬 {title}", key=f"sess_{s['id']}", use_container_width=True):
                    st.session_state.active_session_id = s["id"]
                    st.session_state.messages = s["messages"]
                    st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        if not st.session_state.confirm_clear:
            if st.button("🗑 Clear History", use_container_width=True):
                st.session_state.confirm_clear = True
                st.rerun()
        else:
            st.warning("Delete all saved conversations? This can't be undone.")
            cc1, cc2 = st.columns(2)
            with cc1:
                if st.button("Cancel", use_container_width=True, key="cancel_clear"):
                    st.session_state.confirm_clear = False
                    st.rerun()
            with cc2:
                if st.button("Delete", use_container_width=True, type="primary", key="confirm_clear_btn"):
                    for fpath in glob.glob(f"{SESSIONS_DIR}/*.json"):
                        os.remove(fpath)
                    st.session_state.messages = []
                    st.session_state.confirm_clear = False
                    st.rerun()

# ============================================================
# HEADER
# ============================================================
top_col1, top_col2 = st.columns([5, 1])
with top_col1:
    st.markdown(f"""
    <div class="nx5-header">
        <div class="nx5-header-title">Customer Support</div>
        <div class="nx5-header-sub">🟢 Online — Nexariza AI Assistant</div>
    </div>
    """, unsafe_allow_html=True)
with top_col2:
    if st.session_state.messages:
        transcript = "\n\n".join(
            f"[{m['time']}] {'You' if m['role']=='user' else 'Nexariza AI'}: {m['content']}"
            for m in st.session_state.messages
        )
        st.download_button("⬇ Export", transcript, file_name="nexariza_support_chat.txt", use_container_width=True)

# ============================================================
# MAIN CHAT
# ============================================================
if not st.session_state.messages:
    st.markdown(f"""
    <div style="text-align:center; padding: 50px 20px 20px 20px;">
        <div style="font-family:'Space Grotesk',sans-serif; font-weight:700; font-size:22px;">Hi! I'm Nexariza AI Support</div>
        <div style="opacity:0.65; font-size:13px; margin-top:6px;">Ask me about our services, pricing, portfolio, or team.</div>
    </div>
    """, unsafe_allow_html=True)
    cols = st.columns(len(SUGGESTIONS))
    for i, s in enumerate(SUGGESTIONS):
        with cols[i]:
            if st.button(s, key=f"suggest_{i}", use_container_width=True):
                chat_end_slot = st.empty()
                handle_question(s)
                st.rerun()
else:
    for idx, msg in enumerate(st.session_state.messages):
        role_class = "user" if msg["role"] == "user" else "bot"
        is_latest_bot = role_class == "bot" and idx == len(st.session_state.messages) - 1

        if role_class == "bot":
            avatar_cls = "nx5-avatar latest" if is_latest_bot else "nx5-avatar"
            avatar_html = mascot_svg(T["accent"], size=40 if is_latest_bot else 34).replace('class="nx5-avatar"', f'class="{avatar_cls}"')
            content_html = render_markdown_lite(msg["content"])
            st.markdown(f"""
            <div class="nx5-msg-row bot">{avatar_html}<div class="nx5-bubble bot">{content_html}</div></div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="nx5-msg-row user"><div class="nx5-bubble user">{msg['content']}</div></div>
            """, unsafe_allow_html=True)

        st.markdown(f"<div class='nx5-timestamp' style='text-align:{'right' if role_class=='user' else 'left'}; margin-{'right' if role_class=='user' else 'left'}: {'12px' if role_class=='user' else '52px'};'>{msg.get('time','')}</div>", unsafe_allow_html=True)

        if msg["role"] == "bot":
            fcol1, fcol2, fcol3 = st.columns([1, 1, 7])
            if msg.get("feedback") is None:
                with fcol1:
                    if st.button("👍", key=f"up_{idx}"):
                        prev_q = st.session_state.messages[idx - 1]["content"] if idx > 0 else ""
                        save_feedback(prev_q, msg["content"], "up")
                        msg["feedback"] = "up"
                        save_session(st.session_state.active_session_id, st.session_state.messages)
                        st.rerun()
                with fcol2:
                    if st.button("👎", key=f"down_{idx}"):
                        prev_q = st.session_state.messages[idx - 1]["content"] if idx > 0 else ""
                        save_feedback(prev_q, msg["content"], "down")
                        msg["feedback"] = "down"
                        save_session(st.session_state.active_session_id, st.session_state.messages)
                        st.rerun()
            else:
                with fcol1:
                    st.caption("Thanks! ✓" if msg["feedback"] == "up" else "Sorry — we'll improve.")

        if msg["role"] == "bot" and (msg["escalate"] or msg.get("feedback") == "down"):
            st.markdown(f"""
            <div class="nx5-escalate">
                Want a real person to follow up on this?
                <a href="mailto:{ESCALATION_CONTACT['email']}">✉ Email us</a>
                <a href="{ESCALATION_CONTACT['whatsapp_link']}" target="_blank">💬 WhatsApp</a>
            </div>
            """, unsafe_allow_html=True)

        if msg["role"] == "bot" and msg.get("followups") and is_latest_bot:
            st.markdown('<div class="nx5-followup-label">You might also ask:</div>', unsafe_allow_html=True)
            fu_cols = st.columns(len(msg["followups"]))
            for i, fu in enumerate(msg["followups"]):
                with fu_cols[i]:
                    if st.button(fu, key=f"followup_{idx}_{i}", use_container_width=True):
                        chat_end_slot = st.empty()
                        handle_question(fu)
                        st.rerun()

chat_end_slot = st.empty()

# ============================================================
# COMPOSER
# ============================================================
user_input = st.chat_input("Type Here...")
if user_input:
    handle_question(user_input)
    st.rerun()