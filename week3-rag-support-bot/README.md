\# Week 3 — RAG-Powered Customer Support Agent



A retrieval-augmented generation (RAG) support bot for Nexariza AI, built on real content from nexariza.com. It answers customer questions using only the company's actual knowledge base, cites its sources, and honestly escalates to a human when it doesn't know the answer instead of guessing.



\## What was required (per the internship roadmap)

\- Ingest Nexariza's website content, FAQs, and service descriptions

\- Answer customer questions accurately using RAG

\- Handle: pricing, services, internship info, contact info

\- Escalate complex queries via WhatsApp/email trigger

\- Provide source citations for every answer



All of the above is implemented in rag\_pipeline.py (core RAG logic) and app.py (chat UI).



Note on tech stack: the roadmap specifies OpenAI Embeddings. I used a free local embedding model (sentence-transformers/all-MiniLM-L6-v2) instead, same reasoning as swapping GPT-4o for Groq in earlier weeks: zero cost, no rate limits, fully offline after the first download. Vector storage uses ChromaDB as specified.



\## What I added beyond the requirement

\- Real content ingested from Nexariza AI's actual live website (About, Services, Portfolio/testimonials, Contact), not placeholder text

\- A calibrated escalation system: tuned against real similarity-score data (not a guessed threshold) so it escalates only when genuinely uncertain, not on every confident answer

\- Source citations shown as expandable cards with the real snippet text used, in plain-language labels (e.g. Services) rather than raw filenames

\- AI-generated follow-up question suggestions after every answer, so the conversation can continue naturally

\- Thumbs up / thumbs down feedback on every answer, logged locally, a real signal for what's working and what isn't

\- Multi-conversation history in the sidebar, grouped by date, with full persistence across sessions

\- Custom Customer Support chat UI with a hand-illustrated mascot that appears beside each reply and bounces while a new answer is being generated

\- Chat export to a downloadable .txt transcript



\## Files

\- app.py, Streamlit chat UI (main deliverable to run)

\- rag\_pipeline.py, core RAG pipeline: ingestion, embeddings, retrieval, escalation logic; also runnable standalone from the terminal

\- knowledge\_base folder, the real Nexariza AI content the bot is grounded on

\- requirements.txt, Python dependencies



\## Setup



1\. Create a virtual environment and activate it:



python -m venv venv

venv\\Scripts\\activate



2\. Install dependencies:



pip install -r requirements.txt



3\. Create a .env file in this folder with your API key:



GROQ\_API\_KEY=your\_key\_here



Free key available at console.groq.com.



4\. Run the chat UI:



streamlit run app.py



Or run the plain terminal version:



python rag\_pipeline.py



On first run, the app builds a local vector database from the knowledge\_base folder (downloads a small embedding model once, then works fully offline).



\## Screenshots



!\[Answering a services question with sourced info](./screenshots/demo1.png)

!\[Follow-up question suggestions](./screenshots/demo2.png)

!\[Honest escalation when the bot does not know something](./screenshots/demo3.png)

