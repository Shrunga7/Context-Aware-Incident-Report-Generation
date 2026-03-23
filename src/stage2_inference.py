from transformers import T5ForConditionalGeneration, T5Tokenizer
import torch
import pandas as pd

MODEL_DIR = "models/flan_t5_stage2"
TEST_PATH = "data/model_ready/test.csv"

tokenizer = T5Tokenizer.from_pretrained(MODEL_DIR)
model = T5ForConditionalGeneration.from_pretrained(MODEL_DIR)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)
model.eval()

test_df = pd.read_csv(TEST_PATH)

sample_df = test_df.head(5).copy()

for i, row in sample_df.iterrows():
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

    prediction = tokenizer.decode(output_ids[0], skip_special_tokens=True)

    print("=" * 80)
    print("INPUT:")
    print(input_text)
    print("\nGROUND TRUTH:")
    print(ground_truth)
    print("\nPREDICTION:")
    print(prediction)
    print("=" * 80)