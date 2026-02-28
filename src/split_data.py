import pandas as pd
from sklearn.model_selection import train_test_split

INP = "data/processed/incident_dataset_stage1.csv"
OUT_DIR = "data/splits"

df = pd.read_csv(INP)

train_df, temp_df = train_test_split(
    df, test_size=0.30, stratify=df["incident_type"], random_state=42 # 70% train, 15% val, 15% test
)
val_df, test_df = train_test_split(
    temp_df, test_size=0.50, stratify=temp_df["incident_type"], random_state=42
)

train_df.to_csv(f"{OUT_DIR}/train.csv", index=False)
val_df.to_csv(f"{OUT_DIR}/val.csv", index=False)
test_df.to_csv(f"{OUT_DIR}/test.csv", index=False)

print("Train:", len(train_df), "Val:", len(val_df), "Test:", len(test_df))
print("\nTrain type counts:\n", train_df["incident_type"].value_counts())