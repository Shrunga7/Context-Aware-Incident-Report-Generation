# from transformers import T5ForConditionalGeneration, T5Tokenizer
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch
import pandas as pd
import evaluate

MODEL_DIR = "models/flan_t5_stage2"
TEST_PATH = "data/model_ready/test.csv"

# tokenizer = T5Tokenizer.from_pretrained(MODEL_DIR)
# model = T5ForConditionalGeneration.from_pretrained(MODEL_DIR)
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_DIR)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

test_df = pd.read_csv(TEST_PATH)

rouge = evaluate.load("rouge")

predictions = []
references = []

# Store predictions for reuse
all_outputs = []

for _, row in test_df.iterrows():
    input_text = row["input_text"]
    ground_truth = row["target_text"]

    inputs = tokenizer(
        input_text,
        return_tensors="pt",
        truncation=True,
        max_length=64
    ).to(device)

    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=96,
            num_beams=4,
            repetition_penalty=1.2,
            no_repeat_ngram_size=3,
            early_stopping=True
        )

    prediction = tokenizer.decode(output_ids[0], skip_special_tokens=True).strip() 

    predictions.append(prediction)
    references.append(ground_truth.strip())

    # store for later printing
    all_outputs.append((input_text, ground_truth, prediction))

# 🔹 ROUGE evaluation
results = rouge.compute(predictions=predictions, references=references)

print("\nROUGE Evaluation on Test Set")
print(f"ROUGE-1:   {results['rouge1']:.4f}")
print(f"ROUGE-2:   {results['rouge2']:.4f}")
print(f"ROUGE-L:   {results['rougeL']:.4f}")
print(f"ROUGE-Lsum:{results['rougeLsum']:.4f}")

# 🔹 Show sample predictions
print("\nSample Predictions:\n")

for i in range(5):
    input_text, ground_truth, prediction = all_outputs[i]

    print("=" * 80)
    print("INPUT:")
    print(input_text)
    print("\nGROUND TRUTH:")
    print(ground_truth)
    print("\nPREDICTION:")
    print(prediction)
    print("=" * 80)