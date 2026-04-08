import os
import numpy as np
import pandas as pd
from datasets import Dataset # Refers to Hugging Face Datasets library
import evaluate

from transformers import (
    T5Tokenizer,
    T5ForConditionalGeneration,
    DataCollatorForSeq2Seq,
    Seq2SeqTrainingArguments,
    Seq2SeqTrainer,
)

# =========================================================
# STEP 1: File paths
# =========================================================
TRAIN_PATH = "data/model_ready/train.csv"
VAL_PATH = "data/model_ready/val.csv"
TEST_PATH = "data/model_ready/test.csv"
OUTPUT_DIR = "models/flan_t5_stage2"

# =========================================================
# STEP 2: Model choice
# =========================================================
# Start with flan-t5-small. Later can try base if needed.
MODEL_NAME = "google/flan-t5-small"

# =========================================================
# STEP 3: Load CSV files
# =========================================================
train_df = pd.read_csv(TRAIN_PATH)
val_df = pd.read_csv(VAL_PATH)
test_df = pd.read_csv(TEST_PATH)

# Handling missing Values (if any)
for name, d in zip(["Train", "Val", "Test"], [train_df, val_df, test_df]):
    if d.isnull().any().any():
        print(f"Warning: Missing values found in {name} dataset!")
        print(d.isnull().sum())
    else:
        print(f"No missing values in {name} dataset.")

print("Train rows:", len(train_df)) # 210 rows
print("Val rows:", len(val_df))     # 45 rows
print("Test rows:", len(test_df))   # 45 rows

# =========================================================
# STEP 4: Convert pandas DataFrames to Hugging Face Datasets
# =========================================================
train_ds = Dataset.from_pandas(train_df.reset_index(drop=True))
val_ds = Dataset.from_pandas(val_df.reset_index(drop=True))
test_ds = Dataset.from_pandas(test_df.reset_index(drop=True))

# print("train_ds:", train_ds)

# =========================================================
# STEP 5: Load tokenizer and model
# =========================================================
tokenizer = T5Tokenizer.from_pretrained(MODEL_NAME) # loads the tokenizer for T5 model. Used to convert text into token IDs that the model can understand.
model = T5ForConditionalGeneration.from_pretrained(MODEL_NAME) # model's weights and layers are loaded. the token IDs are used

# =========================================================
# STEP 6: Define tokenization settings
# =========================================================
MAX_INPUT_LEN = 64 # 95th percentile of i/p data had token length of 39. 64 is a safe buffer to capture all input text without truncation. Longer lengths increase training time and memory usage. So, we want to keep it as low as possible while still capturing most of the data.
MAX_TARGET_LEN = 96 # 95th percentile of o/p data had token length of 64. 96 is a safe buffer to capture all target text without truncation. Longer lengths increase training time and memory usage. So, we want to keep it as low as possible while still capturing most of the data.


# =========================================================
# STEP 7: Preprocessing function
# =========================================================
# This converts text into token IDs for the model.
def preprocess_function(examples):
    # Tokenize the input side
    model_inputs = tokenizer(
        examples["input_text"],
        max_length=MAX_INPUT_LEN,
        truncation=True,
        padding="max_length",
    )

    # Tokenize the target side
    labels = tokenizer(
        text_target=examples["target_text"],
        max_length=MAX_TARGET_LEN,
        truncation=True,
        padding="max_length",
    )

    model_inputs["labels"] = labels["input_ids"]
    return model_inputs

# Apply tokenization to train/val/test sets 
tokenized_train = train_ds.map(preprocess_function, batched=True)
tokenized_val = val_ds.map(preprocess_function, batched=True)
tokenized_test = test_ds.map(preprocess_function, batched=True)

# =========================================================
# STEP 8: Data collator
# =========================================================
# Helps batch sequences properly during training.
data_collator = DataCollatorForSeq2Seq(
    tokenizer=tokenizer,
    model=model,
)
# =========================================================
# STEP 9: Evaluation metric
# =========================================================
rouge = evaluate.load("rouge") # Automatically computes ROUGE-1, ROUGE-2, ROUGE-L, and ROUGE-Lsum scores.
# ROUGE score is used to evaluate text generation tasks.
# If 1.0 (100%), model's o/p is identical to Human-written text.

def compute_metrics(eval_preds):
    predictions, labels = eval_preds

    # Some trainer versions return tuples
    if isinstance(predictions, tuple):
        predictions = predictions[0]

    # Ensure predictions are valid token ids
    predictions = np.array(predictions)
    labels = np.array(labels)

    # Replace any negative values in predictions with pad token id
    predictions = np.where(predictions < 0, tokenizer.pad_token_id, predictions)

    # Replace ignored label tokens (-100) so labels can be decoded
    labels = np.where(labels != -100, labels, tokenizer.pad_token_id)

    # Decode predictions and references
    decoded_preds = tokenizer.batch_decode(predictions, skip_special_tokens=True)
    decoded_labels = tokenizer.batch_decode(labels, skip_special_tokens=True)

    decoded_preds = [pred.strip() for pred in decoded_preds]
    decoded_labels = [label.strip() for label in decoded_labels]

    result = rouge.compute(predictions=decoded_preds, references=decoded_labels)
    result = {k: round(v, 4) for k, v in result.items()}
    return result

# =========================================================
# STEP 10: Training arguments (tells the hugging face trainer how to train the model)
# =========================================================
training_args = Seq2SeqTrainingArguments(
    output_dir=OUTPUT_DIR,
    eval_strategy="epoch",       # evaluate model, save checkpoints, print progress after every epoch.
    save_strategy="epoch",
    logging_strategy="epoch",
    learning_rate=3e-4,
    per_device_train_batch_size=8, # model looks at 8 pairs(i/p text, target text) at a time before updating weights.
    per_device_eval_batch_size=8,
    num_train_epochs=5,
    weight_decay=0.01,          # subtracts 0.01 from weights. Helps prevent overfitting by discouraging large weights.
    predict_with_generate=True, # writes new txt while evaluating. Crucial for ROUGE calculation.
    fp16=False,                  # set True uses 16-bit precision and false uses 32-bit. GPU supports it well also for larger datasets.
    save_total_limit=2,
    load_best_model_at_end=True, # Automatically load best model after training based on rouge-L score
    metric_for_best_model="rougeL", 
    greater_is_better=True,
    report_to="none",            # Disables auto-logging to WandB or TensorBoard.
)

# =========================================================
# STEP 11: Create trainer that trains the model
# =========================================================
trainer = Seq2SeqTrainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_train,
    eval_dataset=tokenized_val,     # Whenever you evaluate, use tokenized_val
    processing_class=tokenizer,
    data_collator=data_collator,
    compute_metrics=compute_metrics,
)

# =========================================================
# STEP 12: Train the model
# =========================================================
print("\nStarting training...\n")
trainer.train() # Training is finished here

# =========================================================
# STEP 13: Save final model and tokenizer
# =========================================================
trainer.save_model(OUTPUT_DIR)          # BEST MODEL is saved(based on validation ROUGE-L) due to load_best_model_at_end=True in training_args
tokenizer.save_pretrained(OUTPUT_DIR)  # saves the tokenizer config and vocab files

print(f"\nModel saved to: {OUTPUT_DIR}")

# =========================================================
# STEP 14: Evaluate on validation set
# =========================================================
print("\nValidation results:")
val_results = trainer.evaluate()
print(val_results)

# # =========================================================
# # STEP 15: Evaluate on test set
# # =========================================================
# print("\nTest results:")
# test_results = trainer.evaluate(eval_dataset=tokenized_test)
# print(test_results)

# # =========================================================
# # STEP 16: Generate sample predictions from test set
# # =========================================================
# print("\nSample predictions:\n")

# sample_df = test_df.head(5).copy()

# for i, row in sample_df.iterrows():
#     inputs = tokenizer(
#         row["input_text"],
#         return_tensors="pt",
#         truncation=True,
#         max_length=MAX_INPUT_LEN,
#     )

#     output_ids = model.generate(
#         **inputs,
#         max_length=MAX_TARGET_LEN,
#         num_beams=4,
#         early_stopping=True,
#     )

#     prediction = tokenizer.decode(output_ids[0], skip_special_tokens=True)

#     print("=" * 80)
#     print("INPUT:")
#     print(row["input_text"])
#     print("\nGROUND TRUTH:")
#     print(row["target_text"])
#     print("\nPREDICTION:")
#     print(prediction)
#     print("=" * 80)




#---------------------tokenization settings
# df = pd.read_csv("data/model_ready/train.csv")

# MAX_INPUT_LEN = 64
# MAX_TARGET_LEN = 96

# input_lengths = []
# target_lengths = []

# for _, row in df.iterrows():
#     input_len = len(tokenizer(row["input_text"])["input_ids"])
#     target_len = len(tokenizer(row["target_text"])["input_ids"])

#     input_lengths.append(input_len)
#     target_lengths.append(target_len)

# print("Input length stats:")
# print("Max:", max(input_lengths))
# print("95th percentile:", int(np.percentile(input_lengths, 95))) # max= 39, 95% of data <=39. So,  MAX_INPUT_LEN = 64

# print("\nTarget length stats:")
# print("Max:", max(target_lengths))
# print("95th percentile:", int(np.percentile(target_lengths, 95))) # max = 74, 95% of data <=69. So, MAX_TARGET_LEN = 96
