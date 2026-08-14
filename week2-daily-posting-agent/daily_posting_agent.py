"""
Nexariza AI Internship — Week 2
Daily Content Posting Agent — Core Pipeline
(imported by app.py for the dashboard UI)
"""

import os
import json
import random
from datetime import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults

load_dotenv()

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0.7)
search_tool = TavilySearchResults(max_results=8)

NEXARIZA_BRAND_CONTEXT = """
You are creating content for Nexariza AI, an agentic AI solutions company that
builds real-world autonomous AI systems for businesses. The tone should be
professional, forward-thinking, and confident — but not overly salesy.
Always represent Nexariza AI positively and naturally weave in the brand name.
"""

TOPIC_QUERY_VARIANTS = [
    "latest AI breakthroughs this week",
    "trending artificial intelligence news today",
    "new AI agent frameworks and tools 2026",
    "AI industry announcements this week",
    "latest LLM and machine learning research news",
    "AI startup funding and product launches this week",
]

TOPIC_HISTORY_FILE = "used_topics.json"
RESEARCH_DOMAINS = {
    "arxiv.org": "research", "openai.com": "research", "anthropic.com": "research",
    "techcrunch.com": "news", "theverge.com": "news", "reuters.com": "news",
    "bloomberg.com": "news", "wired.com": "news", "venturebeat.com": "news",
}


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


def classify_domain(url: str) -> str:
    for domain, category in RESEARCH_DOMAINS.items():
        if domain in url:
            return category
    return "industry"


def research_topic(topic_override: str = None) -> dict:
    """
    Search the web for a trending AI/tech topic (or use the given one),
    and return the sources actually used — real data, no invented scores.
    """
    query = random.choice(TOPIC_QUERY_VARIANTS)
    results = search_tool.invoke(query)

    sources = []
    if isinstance(results, list):
        for item in results:
            if isinstance(item, dict) and "url" in item:
                url = item.get("url", "")
                sources.append({
                    "title": item.get("title", url),
                    "url": url,
                    "domain": url.split("/")[2] if "://" in url else url,
                    "category": classify_domain(url),
                })

    if topic_override:
        selected_topic = topic_override
    else:
        recently_used = load_used_topics()
        avoid_text = ""
        if recently_used:
            avoid_text = (
                "\n\nDo NOT pick any of these topics or very similar stories, "
                "since they were already used recently:\n- " + "\n- ".join(recently_used)
            )
        prompt = f"""
        Here are recent AI/tech news search results:
        {results}

        Pick ONE interesting, specific, and postable trending topic from these
        results. Respond with ONLY the topic as a short phrase (max 12 words),
        nothing else.{avoid_text}
        """
        selected_topic = llm.invoke(prompt).content.strip()
        save_used_topic(selected_topic)

    return {
        "selected_topic": selected_topic,
        "sources": sources,
        "scanned_at": datetime.now().strftime("%H:%M:%S"),
    }


def generate_linkedin_post(topic: str) -> str:
    prompt = f"""{NEXARIZA_BRAND_CONTEXT}

    Write a professional LinkedIn post (150-200 words) about: "{topic}"

    Structure: a strong hook line, 2-3 short paragraphs of insight or
    commentary, and a closing thought. Mention Nexariza AI naturally once.
    End with 3-4 relevant hashtags on their own line.
    """
    return llm.invoke(prompt).content.strip()


def generate_instagram_caption(topic: str) -> dict:
    prompt = f"""{NEXARIZA_BRAND_CONTEXT}

    Write an Instagram caption (2-4 short sentences, casual but smart tone)
    about: "{topic}". Mention Nexariza AI naturally.

    Then on a new line, provide exactly 8 relevant hashtags separated by spaces.
    Prefix that line with "HASHTAGS:".
    """
    raw = llm.invoke(prompt).content.strip()
    if "HASHTAGS:" in raw:
        caption, hashtags_raw = raw.split("HASHTAGS:", 1)
    else:
        caption, hashtags_raw = raw, ""

    words = hashtags_raw.replace(",", " ").split()
    clean_tags = []
    for w in words:
        tag = w.strip().lstrip("#")
        if tag:
            clean_tags.append(f"#{tag}")

    return {"caption": caption.strip(), "hashtags": " ".join(clean_tags)}


def generate_twitter_thread(topic: str) -> list:
    prompt = f"""{NEXARIZA_BRAND_CONTEXT}

    Write a Twitter/X thread of exactly 4 tweets about: "{topic}".
    Each tweet must be under 280 characters. Mention Nexariza AI naturally
    in one of the tweets. Number them 1/, 2/, 3/, 4/ at the start of each.

    Respond with each tweet on its own line, nothing else.
    """
    raw = llm.invoke(prompt).content.strip()
    tweets = [line.strip() for line in raw.split("\n") if line.strip()]
    return tweets


def save_daily_report(report: dict) -> str:
    os.makedirs("daily_reports", exist_ok=True)
    filename = f"daily_reports/report_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    return filename


if __name__ == "__main__":
    user_topic = input("Enter a topic (or press Enter to auto-discover): ").strip()
    research = research_topic(topic_override=user_topic if user_topic else None)
    print(f"\n📌 Topic: {research['selected_topic']}\n")

    linkedin = generate_linkedin_post(research["selected_topic"])
    instagram = generate_instagram_caption(research["selected_topic"])
    twitter = generate_twitter_thread(research["selected_topic"])

    report = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "topic": research["selected_topic"],
        "sources": research["sources"],
        "linkedin_post": linkedin,
        "instagram": instagram,
        "twitter_thread": twitter,
    }
    path = save_daily_report(report)

    print("=" * 60)
    print("LINKEDIN POST:\n", linkedin)
    print("=" * 60)
    print("INSTAGRAM:\n", instagram["caption"])
    print("Hashtags:", instagram["hashtags"])
    print("=" * 60)
    print("TWITTER THREAD:")
    for tweet in twitter:
        print(tweet)
    print("=" * 60)
    print(f"✅ Saved to {path}")