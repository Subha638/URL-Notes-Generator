import streamlit as st
from scraper import extract_text_from_url
from notes_generator import generate_notes, generate_faq, generate_mcq
from pdf_export import create_pdf
import os
import uuid

st.set_page_config(page_title="AI URL-to-Notes Generator", layout="wide")

st.title("📘 AI URL → Clean Notes Generator (Advanced)")
st.write("Paste any webpage link to generate notes, summary, FAQs, and MCQs.")

url = st.text_input("Enter URL:")

if st.button("Generate Notes"):
    with st.spinner("Extracting content..."):
        article = extract_text_from_url(url)

    if not article:
        st.error("Could not extract content. Try another URL.")
    else:
        st.success("Content extracted successfully!")

        with st.spinner("Generating structured study notes..."):
            notes = generate_notes(article)
            faq = generate_faq(article)
            mcq = generate_mcq(article)

        st.subheader("📄 Clean Notes")
        st.write(notes)

        st.subheader("❓ FAQs")
        st.write(faq)

        st.subheader("📝 MCQs")
        st.write(mcq)

        # PDF Export
        filename = f"notes_{uuid.uuid4().hex}.pdf"
        create_pdf(notes, faq, mcq, filename)

        with open(filename, "rb") as f:
            st.download_button("Download PDF", f, file_name="AI_Notes.pdf")

        os.remove(filename)
