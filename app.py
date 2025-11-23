import streamlit as st
import os
import requests

# Load API key from environment variable (must be set in Streamlit Cloud dashboard)
API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    st.error("❌ API key missing! Set OPENAI_API_KEY in Streamlit Secrets.")
    st.stop()

API_URL = "https://api.openai.com/v1/chat/completions"

def generate_notes_from_url(url):
    prompt = f"Extract clear, structured notes from the following URL:\n{url}\n\nProvide bullet points, headings, and summary."

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(API_URL, headers=headers, json=data)

    if response.status_code != 200:
        return f"❌ Error: {response.text}"

    result = response.json()
    notes = result["choices"][0]["message"]["content"]
    return notes

st.title("URL → Smart Notes Extractor")
st.write("Paste any article URL to generate clean, easy-to-read notes.")

url_input = st.text_input("Enter URL")

if st.button("Generate Notes"):
    if url_input:
        with st.spinner("Generating notes..."):
            output = generate_notes_from_url(url_input)
            st.write(output)
    else:
        st.warning("Please enter a URL!")
