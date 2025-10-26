from transformers import BartTokenizer, BartForConditionalGeneration

def load_summarizer(model_path="./fine_tuned_bart_large_cnn"):
    tokenizer = BartTokenizer.from_pretrained(model_path)
    model = BartForConditionalGeneration.from_pretrained(model_path)
    return tokenizer, model

def summarize_text(tokenizer, model, text, max_input_len=512, max_output_len=128):
    inputs = tokenizer([text], max_length=max_input_len, truncation=True, return_tensors="pt")
    summary_ids = model.generate(
        inputs["input_ids"],
        num_beams=4,
        length_penalty=2.0,
        max_length=max_output_len,
        min_length=30,
        no_repeat_ngram_size=3,
        early_stopping=True
    )
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return summary
