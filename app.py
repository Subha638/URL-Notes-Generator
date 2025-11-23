# app.py
import streamlit as st
from pathlib import Path
import time
import os

from utils import extract_text_from_url, generate_notes_with_openai, generate_notes_fallback
from utils import generate_faqs_with_openai, generate_faqs_fallback
from utils import generate_mcqs_with_openai, generate_mcqs_fallback
from pdf_utils import create_pdf_bytes

st.set_page_config(page_title="URL → Smart Notes", layout="wide")

st.title("📚 URL → Smart Notes (Summary • Notes • FAQ • MCQs • PDF)")
st.markdown(
    "Paste a webpage URL and get clean summary notes, FAQ, multiple-choice questions (MCQs), and a downloadable PDF. "
    "For best results connect your OpenAI API key in the sidebar."
)

# Sidebar: settings
st.sidebar.header("Settings & API keys")
openai_key = st.sidebar.text_input("OpenAI API Key (optional)", type="password")
if openai_key:
    os.environ["OPENAI_API_KEY"] = openai_key

num_bullets = st.sidebar.slider("Number of bullet points (notes)", 3, 12, 6)
num_faq = st.sidebar.slider("Number of FAQs", 1, 10, 5)
num_mcq = st.sidebar.slider("Number of MCQs", 1, 10, 5)
max_tokens = st.sidebar.slider("Max tokens for LLM (if used)", 200, 1500, 600)

st.sidebar.markdown("---")
st.sidebar.markdown(
    "Tip: Provide an OpenAI key for high-quality notes & MCQs. If not provided the app uses a local fallback summarizer."
)

# Main UI
url = st.text_input("Paste a URL to extract notes from", "")

col1, col2 = st.columns([3,1])
with col1:
    if st.button("Generate Notes"):
        if not url.strip():
            st.warning("Please paste a URL first.")
        else:
            with st.spinner("Fetching and processing the webpage..."):
                try:
                    raw_text = extract_text_from_url(url)
                except Exception as e:
                    st.error(f"Failed to extract text from URL: {e}")
                    raw_text = ""
                if not raw_text or len(raw_text.strip()) < 200:
                    st.error("Couldn't extract enough textual content from the URL. Try another page.")
                else:
                    # Use OpenAI if key present
                    use_openai = bool(os.environ.get("OPENAI_API_KEY"))
                    if use_openai:
                        # Notes
                        notes = generate_notes_with_openai(raw_text, bullets=num_bullets, max_tokens=max_tokens)
                        faqs = generate_faqs_with_openai(raw_text, count=num_faq, max_tokens=max_tokens)
                        mcqs = generate_mcqs_with_openai(raw_text, count=num_mcq, max_tokens=max_tokens)
                    else:
                        notes = generate_notes_fallback(raw_text, bullets=num_bullets)
                        faqs = generate_faqs_fallback(raw_text, count=num_faq)
                        mcqs = generate_mcqs_fallback(raw_text, count=num_mcq)
                    st.success("Generated!")
                    st.markdown("---")
                    st.header("📄 Summary / Notes")
                    st.write(notes["summary"])
                    st.markdown("**Key bullet points:**")
                    for i, b in enumerate(notes["bullets"], 1):
                        st.write(f"{i}. {b}")
                    st.markdown("---")
                    st.header("❓ FAQs (Auto-generated)")
                    for i, qa in enumerate(faqs, 1):
                        st.write(f"**Q{i}. {qa['q']}**")
                        st.write(f"- A: {qa['a']}")
                    st.markdown("---")
                    st.header("✏️ MCQs (Auto-generated)")
                    for i, mcq in enumerate(mcqs, 1):
                        st.write(f"**Q{i}. {mcq['question']}**")
                        for idx, opt in enumerate(mcq["options"], 1):
                            st.write(f"- {chr(64+idx)}. {opt}")
                        st.write(f"**Answer:** {mcq['answer']}")
                    st.markdown("---")

                    # Provide PDF download
                    pdf_bytes = create_pdf_bytes(
                        title=f"Notes - {url}",
                        url=url,
                        summary=notes["summary"],
                        bullets=notes["bullets"],
                        faqs=faqs,
                        mcqs=mcqs
                    )
                    st.download_button(
                        label="Download study pack (PDF)",
                        data=pdf_bytes,
                        file_name="study_pack.pdf",
                        mime="application/pdf"
                    )
    else:
        st.info("Paste a URL and click **Generate Notes** to begin.")

with col2:
    st.header("Preview / Quick tools")
    st.write("Useful quick actions:")
    st.write("- Try with a blog post or news article")
    st.write("- For research papers, use the paper 'text' view (no PDF)")
    st.write("")
    st.markdown("**Examples to try:**")
    st.markdown(
        "- https://en.wikipedia.org/wiki/Machine_learning  \n"
        "- https://towardsdatascience.com/some-article (replace with any blog you like)  \n"
        "- Any news article URL"
    )
    st.markdown("---")
    st.write("Status:")
    st.write(f"OpenAI available: {'Yes' if os.environ.get('OPENAI_API_KEY') else 'No (fallback enabled)'}")

st.markdown("\n---\nBuilt for hackathons • Simple to extend (chatbot, highlights, multi-language).")
