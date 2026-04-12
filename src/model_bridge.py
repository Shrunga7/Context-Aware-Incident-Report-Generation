from transformers import T5ForConditionalGeneration, AutoTokenizer
# T5Tokenizer
import torch

MODEL_DIR = "models/flan_t5_stage2" 

print("Loading production inference model...")
# Using AutoTokenizer as defined in your inference_rouge.py
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = T5ForConditionalGeneration.from_pretrained(MODEL_DIR)

# For Shrunga, uncomment the below lines and comment out the above two lines
# tokenizer = T5Tokenizer.from_pretrained(MODEL_DIR)
# model = T5ForConditionalGeneration.from_pretrained(MODEL_DIR)

device = torch.device("cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu")
model.to(device)
model.eval()

def generate_report(incident_text):
    """Takes a single formatted input and runs real-time inference."""
    
    # Using the exact tokenization logic from inference_rouge.py
    inputs = tokenizer(
        incident_text,
        return_tensors="pt",
        truncation=True,
        max_length=64
    )

    # 🚨 Remove token_type_ids if present (inherited from your script)
    inputs.pop("token_type_ids", None)

    # Move all inputs to the correct device
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    with torch.no_grad():
        # The exact generation parameters from your script
        output_ids = model.generate(
            **inputs,
            max_new_tokens=96,
            num_beams=4, # the model tracks the top 4 most likely sequences simultaneously
            repetition_penalty=1.2, # Mathematically discounts the probability of tokens that have already appeared in the output.
            no_repeat_ngram_size=3, # forbids from gen any sequence of 3 tokens from being repeated in the output
            early_stopping=True # tells beam search to stop when 4 complete sentences are found.
        )
        
    return tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()