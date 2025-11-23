import streamlit as st
from openai import OpenAI

# Read API key safely from Streamlit Secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

def ask_model(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def generate_notes(text):
    prompt = f"""
    Convert this content into clean, structured study notes.

    Include:
    - Summary
    - Key points
    - Definitions
    - Important concepts
    - Bullet points

    Content:
    {text}
    """
    return ask_model(prompt)


def generate_faq(text):
    prompt = f"""
    Generate 8 FAQs with detailed answers based on the content:

    {text}
    """
    return ask_model(prompt)


def generate_mcq(text):
    prompt = f"""
    Generate 10 MCQs with 4 options each based on the content.
    Add correct answers at the end.

    Content:
    {text}
    """
    return ask_model(prompt)
