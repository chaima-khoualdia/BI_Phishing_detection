import pandas as pd
from pathlib import Path

# Define paths
processed_folder = Path("data/processed")
fact_phishing_path = processed_folder / "fact_phishing_incident.csv"

# Old aggregate files to delete
old_aggregates = [
    processed_folder / "agg_incidents_per_label.csv",
    processed_folder / "agg_length_stats.csv"
]

# Step 1: Delete old aggregate CSVs if they exist
print("Step 1: Deleting old aggregate CSVs...")
for file_path in old_aggregates:
    if file_path.exists():
        file_path.unlink()
        print(f"  ✅ Deleted: {file_path.name}")
    else:
        print(f"  ℹ️  File not found: {file_path.name}")

# Step 2: Load the fact_phishing_incident data
print("\nStep 2: Loading fact_phishing_incident data...")
df = pd.read_csv(fact_phishing_path)
print(f"  ✅ Loaded {len(df)} rows")

# Step 3: Create aggregate tables
print("\nStep 3: Creating aggregate tables...")

# Aggregate 1: Count of incidents per label
agg_incidents_per_label = df.groupby('label').size().reset_index(name='incident_count')
print(f"  ✅ Created agg_incidents_per_label with {len(agg_incidents_per_label)} rows")
print(f"     {agg_incidents_per_label.to_string(index=False)}")

# Aggregate 2: Length statistics per label
agg_length_stats = df.groupby('label')['length'].agg([
    ('min_length', 'min'),
    ('max_length', 'max'),
    ('mean_length', 'mean'),
    ('median_length', 'median')
]).reset_index()
agg_length_stats['mean_length'] = agg_length_stats['mean_length'].round(2)
agg_length_stats['median_length'] = agg_length_stats['median_length'].round(2)
print(f"  ✅ Created agg_length_stats with {len(agg_length_stats)} rows")
print(f"     {agg_length_stats.to_string(index=False)}")

# Step 4: Save the new aggregate CSVs
print("\nStep 4: Saving aggregate CSVs to data/processed/...")
agg_incidents_per_label.to_csv(processed_folder / "agg_incidents_per_label.csv", index=False)
print(f"  ✅ Saved: agg_incidents_per_label.csv")

agg_length_stats.to_csv(processed_folder / "agg_length_stats.csv", index=False)
print(f"  ✅ Saved: agg_length_stats.csv")

# Step 5: Print confirmations
print("\n=== Summary ===")
print(f"✅ Old aggregate CSVs deleted")
print(f"✅ agg_incidents_per_label.csv created with {len(agg_incidents_per_label)} rows")
print(f"✅ agg_length_stats.csv created with {len(agg_length_stats)} rows")
print(f"✅ All files saved to: {processed_folder.absolute()}")
