"""
Nexariza AI Internship — Week 4
Multi-Agent Research System — Core Pipeline
Researcher -> Analyst -> Writer -> Publisher
"""

import os
import json
import random
from datetime import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults

load_dotenv()

llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0.3)
search_tool = TavilySearchResults(max_results=8)

NEXARIZA_BRAND_CONTEXT = """
You are producing research content for Nexariza AI, an agentic AI solutions company.
The tone should be professional, insightful, and credible — written by people who
genuinely understand the space, not generic AI-generated fluff.
"""

TOPIC_QUERY_VARIANTS = [
    "latest AI breakthroughs this week",
    "trending artificial intelligence news today",
    "new AI agent frameworks and tools 2026",
    "AI industry announcements this week",
]

TOPIC_HISTORY_FILE = "used_research_topics.json"


def load_used_topics() -> list:
    if not os.path.exists(TOPIC_HISTORY_FILE):
        return []
    try:
        with open(TOPIC_HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        return []


def save_used_topic(topic: str):
    history = load_used_topics()
    history.append(topic)
    history = history[-10:]
    with open(TOPIC_HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def discover_trending_topic() -> str:
    """Finds a fresh AI/tech research topic, avoiding recently used ones."""
    query = random.choice(TOPIC_QUERY_VARIANTS)
    results = search_tool.invoke(query)

    recently_used = load_used_topics()
    avoid_text = ""
    if recently_used:
        avoid_text = "\n\nDo NOT pick any of these, they were used recently:\n- " + "\n- ".join(recently_used)

    prompt = f"""
    Here are recent AI/tech search results:
    {results}

    Pick ONE interesting, specific, and researchable trending topic from these
    results. Respond with ONLY the topic as a short phrase (max 12 words),
    nothing else.{avoid_text}
    """
    topic = llm.invoke(prompt).content.strip()
    save_used_topic(topic)
    return topic


# ============================================================
# AGENT 1: RESEARCHER
# ============================================================
def agent_researcher(topic: str) -> dict:
    """Searches the web from multiple angles and collects raw findings + sources."""
    print("🔎 [Researcher] Searching the web for information...")

    queries = [
        topic,
        f"{topic} latest news 2026",
        f"{topic} examples and case studies",
        f"{topic} analysis and trends",
    ]

    all_sources = []
    seen_urls = set()
    combined_findings = ""

    for q in queries:
        results = search_tool.invoke(q)
        if isinstance(results, list):
            for item in results:
                if isinstance(item, dict) and "url" in item:
                    url = item.get("url")
                    if url in seen_urls:
                        continue
                    seen_urls.add(url)
                    all_sources.append({
                        "title": item.get("title", url),
                        "url": url,
                        "content": item.get("content", "")[:400],
                    })
                    combined_findings += f"\n\nSource: {item.get('title', '')}\n{item.get('content', '')[:400]}"

    print(f"✅ [Researcher] Found {len(all_sources)} unique sources across {len(queries)} search angles.")
    return {"topic": topic, "raw_findings": combined_findings, "sources": all_sources}


# ============================================================
# AGENT 2: ANALYST
# ============================================================
def agent_analyst(research: dict) -> dict:
    """Analyzes raw research findings and extracts key insights and structure."""
    print("🧠 [Analyst] Analyzing findings and extracting key insights...")

    prompt = f"""{NEXARIZA_BRAND_CONTEXT}

    Here is raw research gathered on the topic "{research['topic']}":
    {research['raw_findings']}

    Analyze this research and extract:
    1. The 4-6 most important key insights (each 1-2 sentences)
    2. Any notable trends or patterns across the sources
    3. A suggested logical structure for a report on this topic (list of section headers)

    Respond with ONLY valid JSON in this exact format:
    {{
      "key_insights": ["insight 1", "insight 2", "..."],
      "trends": "a short paragraph describing overall trends",
      "suggested_sections": ["section 1", "section 2", "..."]
    }}
    """
    response = llm.invoke(prompt).content.strip()
    response = response.strip("`").replace("json\n", "", 1).strip()

    try:
        analysis = json.loads(response)
    except (json.JSONDecodeError, ValueError):
        analysis = {
            "key_insights": ["Analysis parsing failed — see raw research."],
            "trends": "N/A",
            "suggested_sections": ["Overview", "Key Findings", "Conclusion"],
        }

    print(f"✅ [Analyst] Extracted {len(analysis.get('key_insights', []))} key insights.")
    return analysis


# ============================================================
# AGENT 3: WRITER
# ============================================================
def agent_writer(topic: str, analysis: dict) -> str:
    """Writes a full professional report/blog post based on the analysis."""
    print("✍️  [Writer] Writing the full report...")

    insights_text = "\n".join(f"- {i}" for i in analysis.get("key_insights", []))
    sections_text = ", ".join(analysis.get("suggested_sections", []))

    prompt = f"""{NEXARIZA_BRAND_CONTEXT}

    Write a professional, well-structured research report/blog post on: "{topic}"

    Use these key insights as the foundation:
    {insights_text}

    Overall trends: {analysis.get('trends', '')}

    Structure the report using these sections: {sections_text}

    Requirements:
    - 600-900 words
    - Use markdown headers (##) for each section
    - Professional, confident, insightful tone — not generic AI fluff
    - Include a brief intro and a strong closing thought
    - Naturally mention Nexariza AI's perspective once, where relevant

    IMPORTANT — accuracy constraint:
    - Do NOT invent specific statistics, percentages, benchmark numbers, dates, or
      figures that are not directly present in the key insights or trends above.
    - If you want to make a quantitative-sounding claim, only do so if it is
      genuinely supported by the research provided. Otherwise, use qualitative language
      instead (e.g., "significantly faster" rather than "30% faster", "widely adopted"
      rather than "used by 98% of enterprises").
    - It is better to be vaguer and accurate than specific and fabricated.
    """
    report = llm.invoke(prompt).content.strip()
    print(f"✅ [Writer] Report written ({len(report.split())} words).")
    return report


# ============================================================
# AGENT 4: PUBLISHER
# ============================================================
def agent_publisher(topic: str, report: str) -> dict:
    """Reformats the full report into platform-specific publication formats."""
    print("📤 [Publisher] Formatting for LinkedIn and Medium...")

    linkedin_prompt = f"""{NEXARIZA_BRAND_CONTEXT}

    Here is a full research report on "{topic}":
    {report}

    Condense this into a LinkedIn post (150-200 words). Strong hook line, 2-3 short
    paragraphs of the most compelling insights, a closing thought, and 3-4 relevant
    hashtags on their own line at the end.

    Only use statistics or numbers that already appear in the report above — do not
    introduce new figures. If none are available, use qualitative language instead.
    """
    linkedin_post = llm.invoke(linkedin_prompt).content.strip()

    medium_prompt = f"""{NEXARIZA_BRAND_CONTEXT}

    Here is a full research report on "{topic}":
    {report}

    Format this for Medium publication: add a compelling title (as an H1 # header),
    a one-line subtitle/dek, then the report content with clean markdown formatting
    (## for sections, proper paragraph breaks). Keep all the original content and insights.
    """
    medium_post = llm.invoke(medium_prompt).content.strip()

    print("✅ [Publisher] Formatted for both platforms.")
    return {"linkedin": linkedin_post, "medium": medium_post}


# ============================================================
# FULL PIPELINE (used by the plain terminal version)
# ============================================================
def run_research_pipeline(topic: str) -> dict:
    print(f"\n{'='*60}\n🚀 Starting Multi-Agent Research Pipeline: {topic}\n{'='*60}\n")

    research = agent_researcher(topic)
    analysis = agent_analyst(research)
    report = agent_writer(topic, analysis)
    published = agent_publisher(topic, report)

    result = {
        "topic": topic,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "sources": research["sources"],
        "analysis": analysis,
        "full_report": report,
        "linkedin_post": published["linkedin"],
        "medium_post": published["medium"],
    }

    os.makedirs("generated_reports", exist_ok=True)
    filename = f"generated_reports/report_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}\n✅ Pipeline complete. Saved to {filename}\n{'='*60}\n")
    return result


if __name__ == "__main__":
    topic = input("Enter a research topic (or press Enter for 'Latest AI Agent Frameworks 2025'): ").strip()
    if not topic:
        topic = "Latest AI Agent Frameworks 2025"

    result = run_research_pipeline(topic)

    print("\n" + "=" * 60)
    print("FULL REPORT:\n")
    print(result["full_report"])
    print("\n" + "=" * 60)
    print("LINKEDIN POST:\n")
    print(result["linkedin_post"])
    print("=" * 60)