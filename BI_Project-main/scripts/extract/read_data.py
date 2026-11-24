import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from transform.transform import transform_dataset


project_root = Path(__file__).resolve().parents[2]
raw_data_path = project_root / "data" / "raw" / "urls.csv"
processed_folder = project_root / "data" / "processed"

# Step 1: Delete all existing CSV files in processed folder
if processed_folder.exists():
    for csv_file in processed_folder.glob("*.csv"):
        csv_file.unlink()
        print(f"Deleted: {csv_file.name}")
else:
    processed_folder.mkdir(parents=True, exist_ok=True)

# Step 2: Load raw data
print("\nLoading raw data...")
df_raw = pd.read_csv(raw_data_path)
print(f"Initial rows: {len(df_raw)}")

# Step 3: Transform raw data
df = transform_dataset(df_raw)
print(f"Rows after validation: {len(df)}")

# Final data validation
print("\n=== Final Dataset ===")
print(f"Total rows: {len(df)}")
print(f"\nColumn names:\n{df.columns.tolist()}")
print(f"\nData types:\n{df.dtypes}")
print(f"\nFirst few rows:\n{df.head()}")
print(f"\nPhishing distribution:\n{df['is_phishing'].value_counts()}")

# Save processed data
output_path = processed_folder / "fact_phishing_incident.csv"
df.to_csv(output_path, index=False)
print(f"\nProcessed data saved to: {output_path}")
print(f"Processed data shape: {df.shape}")
