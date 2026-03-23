import pandas as pd
import json
import os

IN_DIR = "data/splits"
OUT_DIR = "data/model_ready"
os.makedirs(OUT_DIR, exist_ok=True)

# Add none to empty fields
def safe_join(value):
    if not value:
        return "None"
    if isinstance(value, list):
        return ", ".join(value) if value else "None"
    return str(value)

# Convert JSON → readable text
def flatten_json(stage1_json, incident_type):
    try:
        sj = json.loads(stage1_json) if isinstance(stage1_json, str) else stage1_json
    except:
        sj = {}

    return f"""
Incident Type: {incident_type}
Services: {safe_join(sj.get('services_affected', []))}
Hosts: {safe_join(sj.get('hosts', []))}
IPs: {safe_join(sj.get('ips', []))}
Commands: {safe_join(sj.get('commands_executed', []))}
""".strip()


# Create target text
def create_target(row):
    return f"""
Root Cause: {row['root_cause']}
Resolution: {row['resolution']}
Preventive Action: {row['preventive_action']}
""".strip()


def process_split(name):
    df = pd.read_csv(f"{IN_DIR}/{name}.csv")

    df["input_text"] = df.apply(
        lambda x: flatten_json(x["stage1_json"], x["incident_type"]), axis=1
    )

    df["target_text"] = df.apply(create_target, axis=1)

    df[["input_text", "target_text"]].to_csv(
        f"{OUT_DIR}/{name}.csv", index=False
    )

    print(f"{name} done:", len(df)) # len(train) = 210, len(val) = 45, len(test) = 45



# Run for all splits
for split in ["train", "val", "test"]:
    process_split(split)
