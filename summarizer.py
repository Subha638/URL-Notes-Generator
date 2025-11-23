from transformers import T5Tokenizer, T5ForConditionalGeneration

tokenizer = T5Tokenizer.from_pretrained("t5-small")
model = T5ForConditionalGeneration.from_pretrained("t5-small")

def generate_notes(text):
    # T5 needs a prefix
    input_text = "summarize: " + text

    inputs = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True)
    summary_ids = model.generate(inputs, max_length=150, min_length=40, length_penalty=2.0, num_beams=4)

    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    # Convert to bullet points
    bullet_points = "• " + summary.replace(". ", ".\n• ")
    return bullet_points
