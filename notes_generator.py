import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def ask_model(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def generate_notes(text):
    prompt = f"""
    Convert the following content into clean structured notes with summary,
    key points, definitions, and bullet points.

    Content:
    {text}
    """
    return ask_model(prompt)


def generate_faq(text):
    prompt = f"""
    Generate 8 FAQs and answers based on the given text:

    {text}
    """
    return ask_model(prompt)


def generate_mcq(text):
    prompt = f"""
    Create 10 MCQs with 4 options each, and provide correct answers at the end.

    Text:
    {text}
    """
    return ask_model(prompt)
