from transformers import pipeline

summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_text(texto):
    max_input_tokens = 1024
    max_output_tokens = 250

    # Truncar por tokens con tokenizer del modelo
    tokenizer = summarizer.tokenizer
    inputs = tokenizer(texto, return_tensors="pt", truncation=True, max_length=max_input_tokens)
    truncated_text = tokenizer.decode(inputs["input_ids"][0], skip_special_tokens=True)

    summary = summarizer(
        truncated_text,
        max_length=max_output_tokens,
        min_length=50,
        do_sample=False,
    )
    return summary[0]["summary_text"]