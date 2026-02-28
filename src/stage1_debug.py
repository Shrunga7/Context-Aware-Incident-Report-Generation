import json
import pandas as pd

from stage1_extraction import (
    normalize_text,
    parse_log_events,
    extract_entities_from_text,
    extract_commands,
    context_fusion,
    validate_extraction
)

INPUT_CSV = "data/raw/incident_dataset.csv"


def debug_single_row(row_index=0):
    df = pd.read_csv(INPUT_CSV)
    row = df.iloc[row_index]

    logs = normalize_text(row.get("logs", ""))
    chat = normalize_text(row.get("chat_transcript", ""))
    commands = normalize_text(row.get("commands_executed", ""))

    print("\n================ RAW INPUT ================")
    print("\n--- LOGS ---\n", logs)
    print("\n--- CHAT ---\n", chat)
    print("\n--- COMMAND ---\n", commands)

    # 1️⃣ Log Parsing & Normalization
    print("\n================ STEP 1: LOG PARSING ================")
    log_events, parse_errors = parse_log_events(logs)

    for e in log_events:
        print(f"Time: {e.time} | Level: {e.level} | Event: {e.event}")

    if parse_errors:
        print("Parse Errors:", parse_errors)

    # 2️⃣ Information Extraction
    print("\n================ STEP 2: ENTITY EXTRACTION ================")
    log_entities = extract_entities_from_text(logs)
    chat_entities = extract_entities_from_text(chat)
    cmd_info = extract_commands(commands)

    print("\nEntities from Logs:")
    print(json.dumps(log_entities, indent=2))

    print("\nEntities from Chat:")
    print(json.dumps(chat_entities, indent=2))

    print("\nCommand Info:")
    print(json.dumps(cmd_info, indent=2))

    # 3️⃣ Context Fusion
    print("\n================ STEP 3: CONTEXT FUSION ================")
    incident_json = context_fusion(log_events, log_entities, chat_entities, cmd_info)
    print(json.dumps(incident_json, indent=2))

    # 4️⃣ Output Evaluation
    print("\n================ STEP 4: VALIDATION ================")
    validation_issues = validate_extraction(incident_json, logs, chat)
    if validation_issues:
        print("Validation Issues:")
        print(validation_issues)
    else:
        print("No validation issues found ✅")

    print("\n================ FINAL JSON ================")
    print(json.dumps(incident_json, indent=2))


if __name__ == "__main__":
    # print("Testing for row 0")
    debug_single_row(row_index=0)  # change index to test other rowsimport json
    # print("Testing for row 1")
    # debug_single_row(row_index=1)  # change index to test other rows
    # print("Testing for row 2")
    # debug_single_row(row_index=2)  # change index to test other rows
    # # df = pd.read_csv(INPUT_CSV)


    # for incident_type in [
    #         "cpu_timeout",
    #         "db_connection_failure",
    #         "security_failed_logins"
    #     ]:
    #         print(f"\n\n\n########## TESTING INCIDENT TYPE: {incident_type.upper()} ##########\n")
    #         sample_row = df[df["incident_type"] == incident_type].iloc[0]
    #         debug_single_row(sample_row)
