# summarizer.py
import os
import json
import textwrap
from typing import Dict, List
from openai import OpenAI
import openai
import re

OPENAI_KEY = os.getenv("OPENAI_API_KEY", None)

# helper simple local summarizer if API key not present
def local_summarize(text: str, max_sentences: int = 6) -> str:
    # naive heuristic: split into sentences and pick the longest ones
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    sentences = [s.strip() for s in sentences if len(s.strip()) > 30]
    sentences_sorted = sorted(sentences, key=lambda s: len(s), reverse=True)
    top = sentences_sorted[:max_sentences]
    return " ".join(top)

def call_openai_chat(prompt: str, model: str = "gpt-4o-mini", max_tokens: int = 1200) -> str:
    if not OPENAI_KEY:
        raise RuntimeError("OPENAI_API_KEY not set")
    # use OpenAI python client
    openai.api_key = OPENAI_KEY
    resp = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that turns article text into study materials."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        temperature=0.2,
    )
    return resp.choices[0].message.content.strip()

def generate_notes_pack(text: str, title: str = "Document", model: str = "gpt-4o-mini", max_tokens: int = 1200) -> Dict:
    """
    Returns a dict with:
    - summary (str)
    - bullets (list)
    - concepts (list)
    - definitions (list of {term, definition})
    - qas (list of {q,a})
    - mcqs (list of {stem, options, answer})
    - flashcards (list of {front, back})
    - raw_text (original raw)
    """
    # Short-circuit fallback
    if not OPENAI_KEY:
        summary = local_summarize(text, max_sentences=6)
        bullets = [summary]
        return {
            "summary": summary,
            "bullets": bullets,
            "concepts": [],
            "definitions": [],
            "qas": [],
            "mcqs": [],
            "flashcards": [],
            "raw_text": text
        }

    # Prepare prompt carefully. We chunk text if huge.
    MAX_CHUNK = 20000  # characters per chunk
    chunks = [text[i:i+MAX_CHUNK] for i in range(0, len(text), MAX_CHUNK)]
    joined_chunks_preview = "\n\n[CHUNK 1 PREVIEW]\n" + (chunks[0][:4096] if chunks else "")

    prompt = f"""
You are an expert educational assistant. Given the article title: "{title}" and the article content (below), produce a JSON object with the following keys:
- summary: a concise 3-5 sentence summary.
- bullets: a list of 6-12 short bullet points (actionable / factual).
- concepts: list of key concept phrases (6-12).
- definitions: list of important terms with short definitions (term and definition).
- qas: 6 short Q&A pairs (question and answer) useful for study.
- mcqs: 6 multiple-choice questions. Each MCQ should have: stem, 4 options, answer (option text).
- flashcards: 8 flashcards with front/back text.
Return ONLY valid JSON. Do not include commentary. The content follows below:
----
{joined_chunks_preview}
----
If the article is long, prioritize the main ideas and educational value. Keep answers short and precise.
"""
    try:
        raw_response = call_openai_chat(prompt, model=model, max_tokens=max_tokens)
        # Expect JSON string; try to load
        # Sometimes model returns markdown — extract JSON block
        json_text = raw_response.strip()
        # attempt to find first { ... } block
        m = re.search(r'(\{.*\})', json_text, flags=re.DOTALL)
        if m:
            json_text = m.group(1)
        data = json.loads(json_text)
    except Exception as e:
        # fallback: minimal local output if parsing failed
        data = {
            "summary": local_summarize(text, max_sentences=5),
            "bullets": [],
            "concepts": [],
            "definitions": [],
            "qas": [],
            "mcqs": [],
            "flashcards": [],
        }

    # keep raw text to enable chatbot Q/A
    data["raw_text"] = text
    return data

def answer_question_about_doc(question: str, doc_text: str, model: str = "gpt-4o-mini", max_tokens: int = 600) -> str:
    if not OPENAI_KEY:
        # simple local search-based answer: find sentences that contain keywords
        import re
        keywords = [w for w in re.findall(r'\w+', question.lower()) if len(w) > 3][:6]
        matches = []
        for kw in keywords:
            idx = doc_text.lower().find(kw)
            if idx != -1:
                start = max(0, idx-200)
                matches.append(doc_text[start:start+400])
        if matches:
            return "Found related passages:\n\n" + "\n\n---\n\n".join(matches[:3])
        return "No API key — simple fallback cannot answer precisely. Generate notes first or set OPENAI_API_KEY."
    # call to LLM with context
    openai.api_key = OPENAI_KEY
    prompt = f"""
You are an expert tutor. Use the provided document context to answer the question concisely. If the document does not contain the answer, say "Not stated in document."

Document (short excerpt or entirety):
\"\"\"\n{doc_text[:30000]}\n\"\"\"

Question: {question}
Answer in 2-8 sentences, cite the part of the document if possible.
"""
    resp = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful tutor."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_tokens,
        temperature=0.1,
    )
    return resp.choices[0].message.content.strip()
