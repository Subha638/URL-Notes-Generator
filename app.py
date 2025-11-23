import streamlit as st
import requests
from bs4 import BeautifulSoup
from summarizer import generate_notes
from pdf_utils import create_pdf

st.title("🔗 URL → Notes Generator (No API Key)")

url = st.text_input("Enter article URL")

if st.button("Generate Notes"):
    try:
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")

        paragraphs = soup.find_all("p")
        article = " ".join([p.text for p in paragraphs])

        if len(article) < 150:
            st.error("Could not extract enough readable text from this URL.")
        else:
            notes = generate_notes(article)

            st.subheader("📝 Notes")
            st.write(notes)

            pdf_path = "notes.pdf"
            create_pdf(notes, pdf_path)

            with open(pdf_path, "rb") as f:
                st.download_button(
                    label="📥 Download PDF",
                    data=f,
                    file_name="notes.pdf",
                    mime="application/pdf"
                )

    except Exception as e:
        st.error(f"❌ Error: {e}")
