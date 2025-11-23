from transformers import PegasusTokenizer, PegasusForConditionalGeneration

model_name = "google/pegasus-xsum"
tokenizer = PegasusTokenizer.from_pretrained(model_name)
model = PegasusForConditionalGeneration.from_pretrained(model_name)

def generate_notes(text):
    # Split long text into manageable chunks
    chunks = []
    current = ""
    words = text.split()

    for w in words:
        if len(current.split()) > 350:
            chunks.append(current)
            current = ""
        current += " " + w
    chunks.append(current)

    final_summary = ""

    for chunk in chunks:
        inputs = tokenizer(chunk, truncation=True, padding="longest", return_tensors="pt")
        summary_ids = model.generate(
            inputs["input_ids"],
            max_length=180,
            min_length=80,
            num_beams=5
        )
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        final_summary += summary + ". "

    # Convert to bullet points
    bullet_points = "• " + final_summary.replace(". ", ".\n• ")
    return bullet_points
