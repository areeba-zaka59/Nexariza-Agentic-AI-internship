"""
Nexariza AI Internship — Week 5
Nexariza Lead Intelligence Agent — Core Pipeline
Discover -> Research -> Score -> Draft Outreach
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
You are a lead qualification assistant for Nexariza AI, an AI consulting and
engineering company that builds custom AI agents, machine learning models,
computer vision systems, automation, and data analytics solutions for
businesses. You are researching potential clients — companies that might
benefit from Nexariza AI's services.
"""

DISCOVERY_QUERY_TEMPLATES = [
    "{industry} companies hiring AI engineers 2026",
    "{industry} startups digital transformation automation",
    "{industry} companies seeking machine learning solutions",
]


def discover_companies(industry: str, target_count: int = 10) -> list:
    """Searches the public web for real companies in the target industry
    that show signals of needing AI/automation solutions."""
    print(f"🔎 [Discovery] Searching for {industry} companies...")

    all_snippets = []
    for template in DISCOVERY_QUERY_TEMPLATES:
        query = template.format(industry=industry)
        results = search_tool.invoke(query)
        if isinstance(results, list):
            for item in results:
                if isinstance(item, dict) and "content" in item:
                    all_snippets.append({
                        "url": item.get("url", ""),
                        "title": item.get("title", ""),
                        "content": item.get("content", "")[:400],
                    })

    combined_text = "\n\n".join(
        f"Source: {s['title']}\nURL: {s['url']}\n{s['content']}" for s in all_snippets
    )

    prompt = f"""{NEXARIZA_CONTEXT}

    Here are web search results about companies in the "{industry}" industry:
    {combined_text}

    From these results, identify up to {target_count} DISTINCT, REAL company
    names mentioned (not generic terms, not Nexariza AI itself). For each
    company, extract a short "signal" — a specific reason from the text why
    they might need AI/automation solutions (e.g. "recently posted job listings
    for ML engineers", "announced a digital transformation initiative").

    Only include companies that are actually named in the text above. Do not
    invent company names. If fewer than {target_count} real companies are
    mentioned, return fewer — do not pad the list with fabricated entries.

    Respond with ONLY valid JSON in this exact format:
    {{
      "companies": [
        {{"company": "Company Name", "signal": "short reason", "source_url": "url"}}
      ]
    }}
    """
    response = llm.invoke(prompt).content.strip()
    response = response.strip("`").replace("json\n", "", 1).strip()

    try:
        parsed = json.loads(response)
        companies = parsed.get("companies", [])
    except (json.JSONDecodeError, ValueError):
        companies = []

    print(f"✅ [Discovery] Identified {len(companies)} real companies.")
    return companies[:target_count]


def research_company(company: dict) -> dict:
    """Runs a targeted search for additional public info on one company."""
    query = f"{company['company']} company news technology AI"
    results = search_tool.invoke(query)

    snippets = []
    if isinstance(results, list):
        for item in results[:3]:
            if isinstance(item, dict) and "content" in item:
                snippets.append(item.get("content", "")[:300])

    company["research_snippet"] = " ".join(snippets)
    return company


def analyze_and_score_lead(company: dict, industry: str) -> dict:
    """Analyzes a company's public info, scores the lead, and drafts outreach."""
    prompt = f"""{NEXARIZA_CONTEXT}

    Company: {company['company']}
    Industry: {industry}
    Initial signal: {company.get('signal', '')}
    Additional public research: {company.get('research_snippet', '')}

    Based ONLY on the information above (do not invent facts about this
    company that aren't supported by the text):

    1. Write a brief needs analysis (2-3 sentences): what AI/automation
       solutions might this company realistically benefit from, based on
       what's actually stated above?
    2. Score this lead as "Hot", "Warm", or "Cold" based on how clear and
       strong the buying signal is. Give a one-sentence reason for the score.
    3. Draft a short, personalized outreach message (100-130 words) from
       Nexariza AI. It should reference the specific signal/context found
       above (not generic flattery), briefly introduce Nexariza AI's
       relevant capability, and end with a soft call to action (e.g.
       suggesting a short call). Professional, not salesy.

       CRITICAL FORMATTING RULES:
       - Start the message with EXACTLY "Hi," on its own line — do NOT include
         a name, placeholder, or bracket like [Name] or [Recipient]. We don't
         know the contact's name, so a plain "Hi," is correct and required.
       - Sign off the email EXACTLY with: "Best regards,\nAreeba Zaka, Nexariza AI"
       - NEVER use placeholders like [Your Name], [Your Title], [Company Name],
         or any bracketed text anywhere in the message.

    Respond with ONLY valid JSON in this exact format:
    {{
      "needs_analysis": "...",
      "score": "Hot",
      "score_reason": "...",
      "outreach_message": "..."
    }}
    """
    response = llm.invoke(prompt).content.strip()
    response = response.strip("`").replace("json\n", "", 1).strip()

    try:
        analysis = json.loads(response)
    except (json.JSONDecodeError, ValueError):
        analysis = {
            "needs_analysis": "Analysis parsing failed.",
            "score": "Cold",
            "score_reason": "Unable to analyze — insufficient parsed data.",
            "outreach_message": "N/A",
        }

    return {**company, **analysis}


def run_lead_pipeline(industry: str, target_count: int = 10) -> list:
    print(f"\n{'='*60}\n🎯 Nexariza Lead Intelligence — Target Industry: {industry}\n{'='*60}\n")

    companies = discover_companies(industry, target_count)
    if not companies:
        print("⚠️  No real companies could be identified from search results. Try a broader industry term.")
        return []

    leads = []
    for i, company in enumerate(companies, start=1):
        print(f"🧠 [{i}/{len(companies)}] Researching and scoring: {company['company']}...")
        enriched = research_company(company)
        lead = analyze_and_score_lead(enriched, industry)
        leads.append(lead)

    os.makedirs("leads", exist_ok=True)
    filename = f"leads/leads_{industry.replace(' ', '_')}_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump({"industry": industry, "date": datetime.now().strftime("%Y-%m-%d"), "leads": leads}, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}\n✅ Pipeline complete. {len(leads)} leads saved to {filename}\n{'='*60}\n")
    return leads


if __name__ == "__main__":
    industry = input("Enter a target industry (e.g. e-commerce, healthcare): ").strip()
    if not industry:
        industry = "e-commerce"

    leads = run_lead_pipeline(industry, target_count=10)

    for i, lead in enumerate(leads, start=1):
        print("\n" + "=" * 60)
        print(f"LEAD {i}: {lead['company']}  —  SCORE: {lead['score']}")
        print("=" * 60)
        print(f"Signal: {lead.get('signal', '')}")
        print(f"Needs Analysis: {lead.get('needs_analysis', '')}")
        print(f"Score Reason: {lead.get('score_reason', '')}")
        print(f"\nOutreach Message:\n{lead.get('outreach_message', '')}")