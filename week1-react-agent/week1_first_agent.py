"""
Nexariza AI Internship 
First ReAct Agent: Web Search + Reasoning
"""

import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent

# Load API keys from .env file
load_dotenv()

# Initialize the LLM (using Groq's free, fast Llama model)
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

# Initialize the web search tool
search_tool = TavilySearchResults(max_results=3)

# Create the ReAct agent with the search tool
agent = create_react_agent(llm, [search_tool])


def ask_agent(question: str):
    """Send a question to the agent and print its final answer."""
    print(f"\n🧠 Question: {question}\n")
    print("🔎 Agent is thinking and searching...\n")

    result = agent.invoke({"messages": [("user", question)]})

    final_message = result["messages"][-1]
    print(f"✅ Answer: {final_message.content}\n")


if __name__ == "__main__":
    # Test the agent with a sample question
    ask_agent("What are the latest AI agent frameworks released in 2025?")

    # You can add more test questions here
    # ask_agent("What is Nexariza AI?")