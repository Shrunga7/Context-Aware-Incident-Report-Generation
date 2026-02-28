1. Dataset is generated using python script incident_generator_dataset.py

2. # In Stage1 extraction, 
* Parsed log events and normalized text, performed NER, extracted commands and perfomed context fusin. 
* Finally Validated the extracted data to maintain factual correctness.

# Debugging
stage1_debug.py

# Testing
stage1_check.py

# Output
Structured JSON (incident_dataset_stage1.csv)

3. # Stage 2 (train model on this JSON → generate full report)

* pip install transformers datasets accelerate sentencepiece evaluate sacrebleu scikit-learn
