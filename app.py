import streamlit as st
import requests
from bs4 import BeautifulSoup
from summarizer import generate_notes
from pdf_utils import create_pdf

st.title("🔗 URL → Detailed Notes Generator (No API Key)")

url = st.text_input("Enter Article URL")

if st.button("Generate Notes"):
    try:
        # FIXED: requests.get() uses timeout= , not request_timeout=
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            st.error("Failed to fetch page. Try another URL.")
            st.stop()

        soup = BeautifulSoup(response.text, "html.parser")

        paragraphs = soup.find_all("p")
        article = " ".join([p.text.strip() for p in paragraphs if len(p.text.strip()) > 20])

        if len(article) < 150:
            st.error("Could not extract sufficient readable text from the URL.")
            st.stop()

        st.info("⏳ Processing article and generating detailed notes...")

        notes = generate_notes(article)

        st.subheader("📝 Generated Notes")
        st.write(notes)

        # Create downloadable PDF
        pdf_path = "notes.pdf"
        create_pdf(notes, pdf_path)

        with open(pdf_path, "rb") as f:
            st.download_button(
                label="📥 Download Notes as PDF",
                data=f,
                file_name="notes.pdf",
                mime="application/pdf"
            )

    except Exception as e:
        st.error(f"❌ Error occurred: {e}")
