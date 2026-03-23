import json
import pandas as pd
from stage1_extraction import stage1_extract_row

INPUT_CSV = "data/raw/incident_dataset.csv"
OUTPUT_CSV = "data/processed/incident_dataset_stage1.csv"

def main():
    df = pd.read_csv(INPUT_CSV)

    stage1_json_list = []
    issues_count = []

    for _, row in df.iterrows():
        incident_json = stage1_extract_row(
            logs=row.get("logs", ""),
            chat=row.get("chat_transcript", ""),
            commands=row.get("commands_executed", "")
        )
        stage1_json_list.append(json.dumps(incident_json, ensure_ascii=False))
        issues_count.append(len(incident_json.get("stage1_validation_issues", [])))

    df["stage1_json"] = stage1_json_list # Contains the fully structured representation of the incident
    df["num_stage1_issues"] = issues_count # Tracks data quality / extraction issues

    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    print(f"✅ Saved: {OUTPUT_CSV}")
    print("Rows:", len(df))
    print("Rows with issues:", sum(i > 0 for i in issues_count))

if __name__ == "__main__":
    main()