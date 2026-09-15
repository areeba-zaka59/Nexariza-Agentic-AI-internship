"""
Nexariza AI Internship — Week 6 (Capstone)
Nexariza Command Center — Backend: 6 integrated AI tools
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.3)
search_tool = TavilySearchResults(max_results=6)

NEXARIZA_CONTEXT = """
You are an AI assistant working for Nexariza AI, an AI consulting and
engineering company that builds custom AI agents, machine learning models,
computer vision, automation, and data analytics for businesses. Be
professional, concise, and accurate. Do not invent specific statistics,
dates, or facts that aren't supported by the information given to you.
"""


# ============================================================
# TOOL 1: MARKET RESEARCH
# ============================================================
def market_research(topic: str) -> dict:
    results = search_tool.invoke(topic)
    sources = []
    combined = ""
    if isinstance(results, list):
        for item in results:
            if isinstance(item, dict) and "url" in item:
                sources.append({"title": item.get("title", ""), "url": item.get("url", "")})
                combined += f"\n\n{item.get('title','')}\n{item.get('content','')[:400]}"

    prompt = f"""{NEXARIZA_CONTEXT}

Research findings on "{topic}":
{combined}

Write a concise market research briefing (300-400 words) covering: current
state, key players/trends mentioned, and one implication for a business
considering this space. Only use facts present in the findings above."""
    summary = llm.invoke(prompt).content.strip()
    return {"summary": summary, "sources": sources}


# ============================================================
# TOOL 2: CONTENT GENERATION
# ============================================================
def generate_content(topic: str) -> dict:
    prompt = f"""{NEXARIZA_CONTEXT}

Generate branded content for Nexariza AI about: "{topic}"

Respond with ONLY valid JSON in this exact format:
{{
  "linkedin": "a 150-200 word LinkedIn post with hashtags",
  "instagram": "a short casual caption with 6-8 hashtags on a new line",
  "twitter": "a 3-tweet thread, numbered 1/ 2/ 3/, each under 280 chars"
}}"""
    response = llm.invoke(prompt).content.strip().strip("`").replace("json\n", "", 1).strip()
    try:
        return json.loads(response)
    except (json.JSONDecodeError, ValueError):
        return {"linkedin": "", "instagram": "", "twitter": ""}


# ============================================================
# TOOL 3: EMAIL DRAFTING
# ============================================================
def draft_email(purpose: str, context: str) -> str:
    prompt = f"""{NEXARIZA_CONTEXT}

Draft a professional client outreach email for Nexariza AI.
Purpose: {purpose}
Context/details to include: {context}

Start with "Hi," (no name placeholder). Sign off as "Areeba Zaka, Nexariza AI".
150-200 words, no bracketed placeholders anywhere."""
    return llm.invoke(prompt).content.strip()


# ============================================================
# TOOL 4: MEETING SUMMARY & ACTION ITEMS
# ============================================================
def summarize_meeting(notes: str) -> dict:
    prompt = f"""{NEXARIZA_CONTEXT}

Here are raw meeting notes:
{notes}

Extract:
1. A concise summary (3-5 sentences)
2. Action items, each with task, owner (or "Unassigned"), deadline (or "TBD"), and priority (High/Medium/Low)

Respond with ONLY valid JSON in this exact format:
{{"summary": "...",
  "action_items": [
    {{"task":"...", "owner":"...", "deadline":"...", "priority":"High"}}
  ]}}"""
    response = llm.invoke(prompt).content.strip().strip("`").replace("json\n", "", 1).strip()
    try:
        return json.loads(response)
    except (json.JSONDecodeError, ValueError):
        return {"summary": "Parsing failed.", "action_items": []}

# ============================================================
# TOOL 5: COMPETITOR ANALYSIS
# ============================================================
def competitor_analysis(company: str) -> dict:
    results = search_tool.invoke(f"{company} competitors alternatives market")
    combined = ""
    if isinstance(results, list):
        for item in results:
            if isinstance(item, dict):
                combined += f"\n\n{item.get('title','')}\n{item.get('content','')[:400]}"

    prompt = f"""{NEXARIZA_CONTEXT}

Search findings about "{company}" and its market:
{combined}

Based ONLY on the findings above, analyze {company} against its named competitors.

Respond with ONLY valid JSON in this exact format:
{{
  "competitors": ["Name1", "Name2", "Name3"],
  "table": {{
    "Product":        {{"company": "...", "comp1": "...", "comp2": "..."}},
    "Pricing":        {{"company": "...", "comp1": "...", "comp2": "..."}},
    "Target Audience":{{"company": "...", "comp1": "...", "comp2": "..."}},
    "Features":       {{"company": "...", "comp1": "...", "comp2": "..."}},
    "Strengths":      {{"company": "...", "comp1": "...", "comp2": "..."}},
    "Weaknesses":     {{"company": "...", "comp1": "...", "comp2": "..."}},
    "AI Capabilities":{{"company": "...", "comp1": "...", "comp2": "..."}},
    "Market Position":{{"company": "...", "comp1": "...", "comp2": "..."}}
  }},
  "advantages": ["..."],
  "weaknesses": ["..."],
  "opportunities": ["..."],
  "threats": ["..."],
  "overall": "3-4 sentence strategic assessment"
}}

If competitors are not clearly named in the findings, use placeholder names like
"Competitor A" and "Competitor B". Do not invent facts about real companies."""

    response = llm.invoke(prompt).content.strip().strip("`").replace("json\n", "", 1).strip()
    try:
        parsed = json.loads(response)
    except (json.JSONDecodeError, ValueError):
        parsed = {
            "competitors": ["Competitor A", "Competitor B"],
            "table": {k: {"company": "—", "comp1": "—", "comp2": "—"}
                      for k in ["Product","Pricing","Target Audience","Features",
                                "Strengths","Weaknesses","AI Capabilities","Market Position"]},
            "advantages": [], "weaknesses": [], "opportunities": [], "threats": [],
            "overall": "Analysis could not be parsed.",
        }
    parsed["company"] = company
    return parsed
# ============================================================
# TOOL 6: TREND MONITORING
# ============================================================
def monitor_trends(industry: str) -> dict:
    results = search_tool.invoke(f"{industry} trends news this week")
    combined = ""
    sources = []
    if isinstance(results, list):
        for item in results:
            if isinstance(item, dict):
                sources.append({"title": item.get("title", ""), "url": item.get("url", "")})
                combined += f"\n\n{item.get('title','')}\n{item.get('content','')[:400]}"

    prompt = f"""{NEXARIZA_CONTEXT}

Search findings on "{industry}" trends:
{combined}

Identify up to 6 distinct, real trends mentioned in the findings above.
For each trend assign:
- "momentum": 0-100
- "growth": percentage 0-100
- "category": one of "Rising", "Emerging", "Peak", "Declining"
- "share": relative 0-100 number (all shares should sum to roughly 100)

Respond with ONLY valid JSON:
{{"trends": [
  {{"trend": "short name", "note": "1-2 sentence explanation",
    "momentum": 82, "growth": 45, "category": "Rising", "share": 22}}
]}}"""
    response = llm.invoke(prompt).content.strip().strip("`").replace("json\n", "", 1).strip()
    try:
        parsed = json.loads(response)
    except (json.JSONDecodeError, ValueError):
        parsed = {"trends": []}
    parsed["sources"] = sources
    return parsed

# ============================================================
# ACTIVITY LOG (shared history across all 6 tools)
# ============================================================
LOG_FILE = "activity_log.json"


def log_activity(tool: str, input_summary: str, output: dict):
    entries = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                entries = json.load(f)
        except (json.JSONDecodeError, ValueError):
            entries = []
    entries.append({
        "tool": tool, "input": input_summary, "output": output,
        "timestamp": datetime.now().isoformat(),
    })
    entries = entries[-100:]
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, ensure_ascii=False, indent=2)


def load_activity() -> list:
    if not os.path.exists(LOG_FILE):
        return []
    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return []