import streamlit as st
import requests
from bs4 import BeautifulSoup
from summarizer import generate_notes
from pdf_utils import create_pdf

st.title("🔗 URL → Notes Generator (No API Key Needed)")

url = st.text_input("Enter any article URL:")

if st.button("Generate Notes"):
    if url.strip() == "":
        st.error("Please enter a valid URL")
    else:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")

            # Extract article text
            paragraphs = soup.find_all("p")
            article = " ".join([p.text for p in paragraphs])

            if len(article) < 200:
                st.error("Unable to extract enough content from this URL.")
            else:
                notes = generate_notes(article)

                st.subheader("📝 Extracted Notes")
                st.write(notes)

                # Save PDF
                pdf_path = "notes.pdf"
                create_pdf(notes, pdf_path)

                with open(pdf_path, "rb") as f:
                    st.download_button("📥 Download Notes as PDF", f, file_name="notes.pdf")

        except Exception as e:
            st.error(f"Error: {e}")
