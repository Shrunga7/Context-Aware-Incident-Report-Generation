# Context-Aware Incident Report Auto-Completion for IT / SOC Teams using NLP

This project focuses on automating the creation of Security Operations Center (SOC) incident reports by transforming heterogeneous, noisy data into structured formats suitable for advanced NLP modeling. We have successfully completed **Stage 1**, which establishes a modular preprocessing pipeline to convert raw multi-source data into a unified JSON representation.

---

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



---

## Roadmap: Stage 2

With a clean and consistent dataset now available, Stage 2 will focus on generative and supervised NLP tasks:

* Automated incident summary generation.


* Auto-completion of structured report fields.


* Severity classification and resolution recommendation modeling.
