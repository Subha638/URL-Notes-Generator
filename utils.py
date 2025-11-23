# utils.py
import os
import trafilatura
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import re
import math

# Optional OpenAI
try:
    import openai
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False

# Fallback summarizer
try:
    from gensim.summarization import summarize as gensim_summarize
except Exception:
    gensim_summarize = None

################################################################################
# Extraction
################################################################################
def extract_text_from_url(url: str) -> str:
    """
    Attempt to extract readable text from a URL using trafilatura first,
    then fallback to requests + BeautifulSoup.
    Returns long continuous text.
    """
    downloaded = trafilatura.fetch_url(url)
    if downloaded:
        txt = trafilatura.extract(downloaded, include_comments=False, include_tables=False, include_formatting=False)
        if txt and len(txt.strip()) > 100:
            return txt

    # Fallback: simple requests + BeautifulSoup text extraction
    r = requests.get(url, timeout=15, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # Remove script/style
    for tag in soup(["script", "style", "header", "footer", "nav", "aside", "form"]):
        tag.decompose()

    # Get visible text
    texts = [t.strip() for t in soup.stripped_strings]
    text = "\n".join(texts)
    # Heuristic: if it's HTML of a PDF viewer or too noisy, return empty
    if len(text) < 200:
        return ""
    return text

################################################################################
# OpenAI helpers
################################################################################
def _ensure_openai_api():
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise RuntimeError("OPENAI_API_KEY not set.")
    if OPENAI_AVAILABLE:
        openai.api_key = key
    else:
        raise RuntimeError("openai package not installed in environment.")

def _call_openai_chat(messages, max_tokens=800, temperature=0.2):
    _ensure_openai_api()
    # Use ChatCompletion (gpt-3.5-turbo or gpt-4 if available)
    model = os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")
    resp = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=float(os.environ.get("OPENAI_TEMP", 0.2))
    )
    return resp["choices"][0]["message"]["content"].strip()

################################################################################
# Notes / summary generation
################################################################################
def generate_notes_with_openai(text: str, bullets: int = 6, max_tokens: int = 600) -> Dict:
    prompt = [
        {"role":"system", "content": "You are a helpful assistant that makes concise study notes."},
        {"role":"user", "content": (
            "Given the following article/text, produce:\n"
            "1) A 2-3 sentence concise summary.\n"
            f"2) {bullets} bullet points listing the most important concepts (short lines).\n"
            "3) 2-3 key definitions (if present).\n\n"
            "Respond in JSON with keys: summary, bullets, definitions.\n\n"
            "ARTICLE:\n\n" + text[:4000]  # truncate long input
        )}
    ]
    try:
        out = _call_openai_chat(prompt, max_tokens=max_tokens)
        # Attempt to parse JSON-ish content; best-effort
        import json, re
        # Find first { ... } block
        m = re.search(r"\{.*\}", out, flags=re.S)
        if m:
            j = m.group(0)
            return json.loads(j)
        else:
            # fallback: simple parse splitting by sections
            lines = out.splitlines()
            summary = lines[0] if lines else ""
            bullets_list = [l.strip("-• ") for l in lines if l.strip().startswith("-")][:bullets]
            return {"summary": summary, "bullets": bullets_list, "definitions": []}
    except Exception as e:
        # in case of failure, fallback to simpler generator
        return generate_notes_fallback(text, bullets=bullets)

def generate_faqs_with_openai(text: str, count: int = 5, max_tokens: int = 600) -> List[Dict[str,str]]:
    prompt = [
        {"role":"system", "content":"You are a helpful assistant that produces FAQs from text."},
        {"role":"user", "content": (
            f"Read the article below and produce {count} frequently asked questions and concise answers. "
            "Return JSON array of objects with keys 'q' and 'a'.\n\n"
            "ARTICLE:\n\n" + text[:4000]
        )}
    ]
    try:
        out = _call_openai_chat(prompt, max_tokens=max_tokens)
        import json, re
        m = re.search(r"(\[.*\])", out, flags=re.S)
        if m:
            return json.loads(m.group(1))
        else:
            # primitive parse: split by Q/A
            pairs = []
            parts = re.split(r"\n(?=Q\d+[:.\)])", out)
            for p in parts[:count]:
                qa = re.split(r"\nA[:.\)]", p, maxsplit=1)
                if len(qa) == 2:
                    q = qa[0].strip()
                    a = qa[1].strip()
                    pairs.append({"q": q, "a": a})
            return pairs
    except Exception:
        return generate_faqs_fallback(text, count=count)

def generate_mcqs_with_openai(text: str, count: int = 5, max_tokens: int = 600) -> List[Dict[str, Any]]:
    prompt = [
        {"role":"system", "content":"You are a helpful assistant that generates multiple-choice questions for studying."},
        {"role":"user", "content": (
            f"From the following article, generate {count} multiple-choice questions (4 options each). "
            "Return JSON array of objects with keys: question, options (array of 4), answer (the correct option text). "
            "Avoid very ambiguous questions.\n\n"
            "ARTICLE:\n\n" + text[:4000]
        )}
    ]
    try:
        out = _call_openai_chat(prompt, max_tokens=max_tokens)
        import json, re
        m = re.search(r"(\[.*\])", out, flags=re.S)
        if m:
            return json.loads(m.group(1))
        else:
            return []
    except Exception:
        return generate_mcqs_fallback(text, count=count)

################################################################################
# Fallback methods (no OpenAI)
################################################################################
def _short_summary(text: str, ratio=0.05):
    if gensim_summarize:
        try:
            s = gensim_summarize(text, ratio=ratio)
            if s and len(s.strip())>20:
                return s
        except Exception:
            pass
    # fallback: take first 3 paragraphs or first 3 sentences
    paragraphs = [p for p in text.split("\n\n") if len(p.strip())>30]
    if paragraphs:
        head = paragraphs[0]
        sentences = re.split(r'(?<=[.!?])\s+', head)
        return " ".join(sentences[:3])
    return text[:500] + "..."

def split_sentences(text):
    sents = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sents if len(s.strip())>20]

def generate_notes_fallback(text: str, bullets: int = 6) -> Dict:
    summary = _short_summary(text, ratio=0.06)
    # pick top N sentences as bullets (heuristic: use first N sentences from first 2 paragraphs)
    paragraphs = [p for p in text.split("\n\n") if len(p.strip())>40]
    bullets_list = []
    if paragraphs:
        candidate = " ".join(paragraphs[:2])
        sents = split_sentences(candidate)
        for s in sents:
            if len(bullets_list) >= bullets:
                break
            bullets_list.append(s.strip())
    # trim bullets length
    bullets_list = [b if len(b) < 200 else b[:200] + "..." for b in bullets_list]
    return {"summary": summary, "bullets": bullets_list, "definitions": []}

def generate_faqs_fallback(text: str, count: int = 5) -> List[Dict[str,str]]:
    # Create simple FAQs by picking top sentences and turning them into Q/A
    sents = split_sentences(text)
    faqs = []
    for i in range(min(count, len(sents)//2)):
        q = sents[i]
        a = sents[i+1] if i+1 < len(sents) else q
        # Make q concise
        if len(q) > 150:
            q = q[:140] + "..."
        faqs.append({"q": f"What is meant by: {q}", "a": a})
    return faqs

def generate_mcqs_fallback(text: str, count: int = 5) -> List[Dict]:
    sents = split_sentences(text)
    mcqs = []
    i = 0
    while len(mcqs) < count and i < len(sents):
        sent = sents[i]
        # find a noun-ish word to mask (simple heuristic: longest word >4 chars)
        words = re.findall(r"\w+", sent)
        candidate = None
        for w in sorted(words, key=lambda x: -len(x)):
            if len(w) > 4 and not w.isdigit():
                candidate = w
                break
        if not candidate:
            i += 1
            continue
        question = sent.replace(candidate, "_____")
        # options: correct and 3 close distractors from other sentences (or permuted substrings)
        options = [candidate]
        # pick distractors
        distractors = []
        j = i+1
        while len(distractors) < 3 and j < len(sents):
            ws = re.findall(r"\w+", sents[j])
            for w in ws:
                if len(w) > 4 and w.lower() != candidate.lower() and w not in distractors:
                    distractors.append(w)
                    if len(distractors) >= 3:
                        break
            j += 1
        # if insufficient distractors, create variants
        while len(distractors) < 3:
            distractors.append(candidate[::-1][:6])  # silly filler
        options.extend(distractors[:3])
        # shuffle options
        import random
        random.shuffle(options)
        mcqs.append({"question": question, "options": options, "answer": candidate})
        i += 2
    return mcqs
