# URL → Notes (Advanced) — Streamlit App

**Features**
- Paste a URL → extract article text (trafilatura / BeautifulSoup)
- Generate: Summary, Bulleted notes, Key concepts, Definitions, Q&A, MCQs, Flashcards
- Chatbot to ask follow-ups about the generated document
- Download notes as PDF
- Streamlit deployment ready

## Requirements
- Python 3.9+
- `OPENAI_API_KEY` environment variable (for full LLM features). Without it a simple fallback summarizer will run.

## Quick Setup (local)
```bash
python -m venv venv
source venv/bin/activate     # Windows: venv\Scripts\activate
pip install -r requirements.txt
export OPENAI_API_KEY="sk-..."
streamlit run app.py
