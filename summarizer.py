# summarizer.py (NEW — fully updated for 2025 OpenAI API)
from openai import OpenAI
import streamlit as st

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def summarize_text(text, model="gpt-4o-mini"):
    if not text.strip():
        return None

    prompt = f"""
You are an academic note generator. Create:

1. Summary
2. Bullet points
3. Key concepts
4. Definitions
5. Q&A (5)
6. MCQs (with answers)
7. Flashcards

Text:
{text}
"""

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Generate structured notes."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )

    return response.choices[0].message["content"]


def answer_question_about_doc(question, document, model="gpt-4o-mini"):
    """Chatbot answer generator for the extracted article."""
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You answer questions only based on the provided article."},
            {"role": "user", "content": f"Article: {document}\n\nQuestion: {question}"},
        ],
        temperature=0.1,
        max_tokens=500,
    )

    return response.choices[0].message["content"]
