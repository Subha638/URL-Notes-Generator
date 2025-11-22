# app.py
import os
import streamlit as st
from pathlib import Path
import time
from extractor import extract_text_from_url
from summarizer import generate_notes_pack
from pdfgen import create_pdf_bytes
from utils import safe_filename

st.set_page_config(page_title="URL → Notes (Advanced)", layout="wide")

st.title("Students HandsOn Note Maker")
st.markdown(
    "Paste a URL and generate: clean notes, bullet summary, key concepts, definitions, Q&A, MCQs, flashcards, and a downloadable PDF. Includes a chatbot to ask follow-ups about the page."
)

# Sidebar config
st.sidebar.header("Settings")
model_choice = st.sidebar.selectbox("LLM model (if available)", ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"], index=0)
max_tokens = st.sidebar.slider("Max tokens for generation", 256, 4096, 1200, step=256)
use_pdf_download = st.sidebar.checkbox("Enable PDF download", value=True)
api_key_env = os.getenv("OPENAI_API_KEY", None)

if not api_key_env:
    st.sidebar.warning("OPENAI_API_KEY not set — falling back to local summarizer (limited output). Set env var for full features.")

# main input
url = st.text_input("Paste a public article / blog / documentation URL here")
generate = st.button("Generate Notes")

# conversation history for chatbot
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if generate and url.strip():
    with st.spinner("Extracting article text..."):
        try:
            raw_text, title = extract_text_from_url(url)
        except Exception as e:
            st.error(f"Failed to fetch or extract URL: {e}")
            raw_text, title = None, None

    if not raw_text or len(raw_text.strip()) < 200:
        st.error("Could not extract sufficient text from the URL. Try another link or check that it's publicly accessible.")
    else:
        st.success(f"Extracted content: {title or 'Untitled'}")
        st.info("Generating notes — this may take a few seconds (depends on LLM).")
        with st.spinner("Generating notes, bullet summary, Q&A, MCQs, flashcards and definitions..."):
            result = generate_notes_pack(
                text=raw_text,
                title=title or "Document",
                model=model_choice,
                max_tokens=max_tokens,
            )

        # Display outputs in tabs
        tabs = st.tabs(["Summary & Bullets", "Key Concepts", "Definitions", "Q&A", "MCQs", "Flashcards", "Raw Text"])
        with tabs[0]:
            st.header("Concise Summary")
            st.write(result.get("summary", "—"))
            st.markdown("**Bullet Points**")
            for b in result.get("bullets", []):
                st.write(f"- {b}")
        with tabs[1]:
            st.header("Key Concepts")
            for c in result.get("concepts", []):
                st.write(f"- {c}")
        with tabs[2]:
            st.header("Important Definitions")
            for d in result.get("definitions", []):
                st.markdown(f"**{d['term']}** — {d['definition']}")
        with tabs[3]:
            st.header("Generated Q&A")
            for i, qa in enumerate(result.get("qas", []), 1):
                st.markdown(f"**Q{i}. {qa['q']}**\n\n> **A:** {qa['a']}")
        with tabs[4]:
            st.header("MCQs (with answers)")
            for i, mcq in enumerate(result.get("mcqs", []), 1):
                st.markdown(f"**Q{i}. {mcq['stem']}**")
                for idx, opt in enumerate(mcq["options"], 1):
                    st.write(f"{idx}. {opt}")
                st.write(f"> **Answer:** {mcq['answer']}")
        with tabs[5]:
            st.header("Flashcards")
            for i, f in enumerate(result.get("flashcards", []), 1):
                st.markdown(f"**Card {i}**: {f['front']}\n\n> {f['back']}")
        with tabs[6]:
            st.header("Raw Extracted Text (truncated)")
            st.text_area("Raw text", value=raw_text[:15000], height=300)

        # Save an artifact to /tmp for PDF creation
        st.session_state.latest_result = result
        st.session_state.latest_title = title or "document"
        st.session_state.latest_url = url

        if use_pdf_download:
            pdf_name = safe_filename(st.session_state.latest_title)[:60] or "notes"
            pdf_bytes = create_pdf_bytes(st.session_state.latest_title, url, result)
            st.download_button(
                label="📥 Download Notes as PDF",
                data=pdf_bytes,
                file_name=f"{pdf_name}.pdf",
                mime="application/pdf",
            )

# Chatbot panel — ask questions about the article
st.markdown("---")
st.header("🤖 Ask about the article (Chatbot)")
col1, col2 = st.columns([3, 1])
with col1:
    user_q = st.text_input("Ask a question about the last generated article (or paste a short excerpt).", key="chat_input")
with col2:
    ask_btn = st.button("Ask")

if ask_btn and user_q.strip():
    if "latest_result" not in st.session_state:
        st.error("Generate notes first from a URL so the chatbot has context.")
    else:
        with st.spinner("Querying LLM for an answer..."):
            from summarizer import answer_question_about_doc
            answer = answer_question_about_doc(
                question=user_q,
                doc_text=st.session_state.latest_result.get("raw_text", "") or "",
                model=model_choice,
                max_tokens=800
            )
        st.session_state.chat_history.append({"q": user_q, "a": answer})
        st.experimental_rerun()

if st.session_state.chat_history:
    st.subheader("Chat history")
    for item in reversed(st.session_state.chat_history[-6:]):
        st.markdown(f"**Q:** {item['q']}")
        st.markdown(f"**A:** {item['a']}")

st.markdown("---")
st.caption("Built for hackathons & learning. Set OPENAI_API_KEY for full LLM capabilities.")
