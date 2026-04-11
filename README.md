# Context-Aware Incident Report Auto-Completion for IT / SOC Teams using NLP

This project focuses on automating the creation of Security Operations Center (SOC) incident reports by transforming heterogeneous, noisy data into structured formats suitable for advanced NLP modeling. We have completed **Stage 1**, which establishes a modular preprocessing pipeline to convert raw multi-source data into a unified JSON representation.

---
## Folder Structure
* Synthetically generated the raw data using incident_generator_dataset.py
* Processed Dataset is generated using the Python script stage1_build_dataset.py
### Stage1 extraction: 
* stage1_extraction.py
* Parsed log events and normalized text, performed NER, extracted commands, and performed context fusion. 
* Finally Validated the extracted data to maintain factual correctness.
### Debugging
* stage1_debug.py
* To debug the functionality of each block of code.
### Testing
* stage1_check.py
* To test any validation failures.
### Stage1 Output
* incident_dataset_stage1.csv
* stage1_json column has Structured JSON representation of the incident.
* num_stage1_issues column tracks the data quality/ extraction issues 
* Example issues: Failed log parsing, Missing entities, Empty fields, Validation failures
### Stage2
1. Performed dataset splits - stage2_generation.py
2. Generated model_ready datasets - model_ready_splits.py
3. Trained the FLAN-T5 model - stage2_train_t5.py
4. Performed model inference - stage2_inference.py
### Streamlit Dashboard
1. UI Dashboard - model_app.py
2. Inference script to generate reports - model_bridge.py

--------------------------------------------------------------------------------------------------

## Overview: Stage 1 Completion

The primary objective of this stage was to normalize and consolidate inconsistent data sources—such as logs, chats, and commands—into a clean dataset (`incident_dataset_stage1.json`) ready for Stage 2 modeling.

### Key Input Sources

The pipeline processes the following fields from each incident record:

* **System Logs:** Timestamped machine events.


* **Chat Transcripts:** Communications between engineers during investigations.


* **Executed Commands:** Terminal commands used for diagnosis.


* **Resolution Details:** Final remediation steps.


* **Preventive Actions:** Measures taken to prevent recurrence.



---

## Methodology & Pipeline

Stage 1 is implemented as a modular NLP preprocessing pipeline consisting of six key components:

1. **Text Normalization:** Standardizes input via lowercasing, noise removal, and whitespace normalization.


2. **Log Parsing:** Extracts structured components like timestamps, log levels (INFO/ERROR), IP addresses, and service names.


3. **Entity Extraction:** Identifies critical units such as hostnames, usernames, file paths, and error codes.


4. **Command Extraction:** Parses terminal activity to identify command names, arguments, and execution frequency.


5. **Context Fusion:** Merges technical evidence and human response actions into a single object while removing duplicate entities.


6. **Validation:** Ensures schema consistency and filters out invalid or empty incidents.

---

## Output Schema

Each processed incident is exported into a structured JSON format:

```json
{
  "incident_id": "INC001",
  "timestamps": [],
  "affected_hosts": [],
  "users": [],
  "services": [],
  "commands_executed": [],
  "errors": [],
  "resolution_steps": [],
  "preventive_actions": [],
  "final_status": ""
}

```

> 
> **Note:** This output serves as the foundational input for all Stage 2 modeling activities.
> 
> 

---

## Current Limitations

While Stage 1 provides a scalable foundation, the following areas are currently out of scope:

* **Rule-Based:** Extraction methods currently rely on rules rather than semantic understanding.


* **No Timeline Reasoning:** Semantic timeline reasoning has not yet been implemented.


* **Manual Inference:** Root-cause inference and severity classification are not automated in this stage.



## Roadmap: Stage 2

With a clean and consistent dataset now available, Stage 2 will focus on generative and supervised NLP tasks:

* Automated incident summary generation.


* Auto-completion of structured report fields.


* Severity classification and resolution recommendation modeling.
