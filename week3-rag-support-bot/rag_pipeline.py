"""
Nexariza AI Internship — Week 3
RAG-Powered Customer Support Agent — Core Pipeline
"""

import os
import glob
from dotenv import load_dotenv
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq

load_dotenv()

KNOWLEDGE_BASE_DIR = "knowledge_base"
VECTOR_DB_DIR = "chroma_db"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

ESCALATION_CONTACT = {
    "email": "contact@nexariza.com",
    "whatsapp": "+92 370 7348001",
    "whatsapp_link": "https://wa.me/923707348001",
}


def build_vector_store():
    """
    Loads all .txt files from knowledge_base/, splits them into chunks,
    embeds them locally (no API cost), and stores them in a persistent
    Chroma vector database.
    """
    print("📚 Loading knowledge base documents...")
    docs = []
    for filepath in sorted(glob.glob(f"{KNOWLEDGE_BASE_DIR}/*.txt")):
        loader = TextLoader(filepath, encoding="utf-8")
        loaded = loader.load()
        for doc in loaded:
            doc.metadata["source"] = os.path.basename(filepath)
        docs.extend(loaded)

    print(f"📄 Loaded {len(docs)} document(s). Splitting into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=80,
        separators=["\n\n", "\n", ". ", " "],
    )
    chunks = splitter.split_documents(docs)
    print(f"✂️  Created {len(chunks)} chunks.")

    print("🧠 Generating embeddings locally (this may take a moment the first time)...")
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)

    print("💾 Building Chroma vector store...")
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTOR_DB_DIR,
    )
    print(f"✅ Vector store built and saved to '{VECTOR_DB_DIR}/'")
    return vectordb


def load_vector_store():
    """Loads an existing vector store from disk without rebuilding it."""
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    return Chroma(persist_directory=VECTOR_DB_DIR, embedding_function=embeddings)


llm = ChatGroq(model="openai/gpt-oss-120b", temperature=0)

SUPPORT_SYSTEM_PROMPT = """You are the official customer support assistant for Nexariza AI,
an AI consulting and engineering company. Answer the user's question using ONLY the
context provided below. Be helpful, professional, and concise.

If the context does not contain enough information to answer confidently, do NOT guess
or make up information. Instead, say you don't have enough information on that specific
point and that you'll flag it for a human team member to follow up.

Context:
{context}

Question: {question}

Answer:"""


def answer_question(vectordb, question: str, k: int = 4) -> dict:
    """
    Retrieves relevant chunks, generates an answer, and determines
    whether the query should be escalated to a human.
    """
    results = vectordb.similarity_search_with_score(question, k=k)

    if not results:
        return {
            "answer": "I don't have information on that yet. Let me connect you with our team.",
            "sources": [],
            "escalate": True,
        }

    context = "\n\n".join([doc.page_content for doc, score in results])
    prompt = SUPPORT_SYSTEM_PROMPT.format(context=context, question=question)
    response = llm.invoke(prompt).content.strip()

    # Escalation heuristic: if the model itself signals it doesn't know,
    # or if the best-matching chunk is a weak semantic match, escalate.
    low_confidence_phrases = [
        "don't have enough information", "not sure", "i don't know",
        "cannot answer", "can't answer", "no information",
    ]
    model_signals_unknown = any(phrase in response.lower() for phrase in low_confidence_phrases)

    best_score = results[0][1]  # lower distance = better match in Chroma's default metric
    weak_match = best_score > 1.55  # tuned from real test data: good matches ~1.0-1.35, weak matches ~1.7+

    escalate = model_signals_unknown or weak_match

    sources = []
    seen = set()
    for doc, score in results:
        src = doc.metadata.get("source", "unknown")
        if src not in seen:
            seen.add(src)
            sources.append({
                "source": src,
                "snippet": doc.page_content[:180],
                "relevance_score": round(float(score), 3),
            })

    return {"answer": response, "sources": sources, "escalate": escalate}

def generate_followups(question: str, answer: str, k: int = 3) -> list:
    """Suggests short, natural follow-up questions based on the conversation so far."""
    prompt = f"""Based on this support conversation, suggest {k} short, natural follow-up
questions a customer might realistically ask next. Each under 8 words. Return ONLY the
questions, one per line, no numbering, no extra text.

Previous question: {question}
Answer given: {answer}
"""
    raw = llm.invoke(prompt).content.strip()
    lines = [l.strip("-• ").strip() for l in raw.split("\n") if l.strip()]
    return lines[:k]
if __name__ == "__main__":
    if not os.path.exists(VECTOR_DB_DIR):
        vectordb = build_vector_store()
    else:
        print("📦 Found existing vector store, loading it...")
        vectordb = load_vector_store()

    print("\n" + "=" * 60)
    print("Nexariza AI Support Bot — Terminal Test")
    print("Type a question, or 'quit' to exit.")
    print("=" * 60 + "\n")

    while True:
        q = input("You: ").strip()
        if q.lower() in ("quit", "exit"):
            break
        if not q:
            continue

        result = answer_question(vectordb, q)
        print(f"\n🤖 Bot: {result['answer']}\n")
        print(f"📎 Sources: {[s['source'] for s in result['sources']]}")
        if result["escalate"]:
            print(f"⚠️  ESCALATION SUGGESTED — Contact: {ESCALATION_CONTACT['email']} | WhatsApp: {ESCALATION_CONTACT['whatsapp']}")
        print()