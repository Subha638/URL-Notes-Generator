from transformers import pipeline

# Load summarizer (free, no API key)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def generate_notes(text):
    # Summarize long text
    summary = summarizer(text, max_length=180, min_length=60, do_sample=False)[0]['summary_text']

    # Convert summary into bullet points
    bullets = summary.replace(". ", ".\n• ")
    return "• " + bullets
