import pandas as pd
import json

# Load processed Stage 1 dataset
df = pd.read_csv("data/processed/incident_dataset_stage1.csv")

print("Total rows:", len(df))

# How many rows have validation issues?
print("Rows with issues:", (df["num_stage1_issues"] > 0).sum())

# Inspect problematic rows
problem_rows = df[df["num_stage1_issues"] > 0]
print(problem_rows.head(3)[["incident_id", "incident_type", "num_stage1_issues"]])

