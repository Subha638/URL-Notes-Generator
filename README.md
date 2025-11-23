# URL → Smart Notes (Streamlit MVP)

**What it does:** Paste a webpage URL and the app extracts the content and auto-generates:
- Concise summary
- Bullet-point notes
- FAQs
- Multiple-choice questions (MCQs)
- Downloadable PDF study pack

**Why:** Great for students, researchers, and hackathons.

---

## Features
- Uses `trafilatura` and `BeautifulSoup` for content extraction.
- Uses **OpenAI** (if `OPENAI_API_KEY` is provided) to generate high-quality notes, FAQs, and MCQs.
- Fallback generators using `gensim` and heuristics if no OpenAI key.
- Streamlit UI with PDF download.

---

## Setup (local)
1. Clone repo
2. Create virtual environment and install:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
