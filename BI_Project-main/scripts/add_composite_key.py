import pandas as pd
import sqlite3
from pathlib import Path

# Load fact table
fact_path = Path("data/processed/fact_phishing_incident.csv")
df_fact = pd.read_csv(fact_path)

# Load characteristics dimension
dim_path = Path("data/processed/dim_url_characteristics.csv")
df_dim = pd.read_csv(dim_path)

print("Creating composite keys for linking...")

# Check for missing columns
print(f"Fact columns: {df_fact.columns.tolist()}")

# Create composite key in fact table - handle missing values
df_fact['characteristic_key'] = (
    df_fact['has_ip'].fillna(0).astype(int).astype(str) + '|' +
    df_fact['has_suspicious_keyword'].fillna(0).astype(int).astype(str) + '|' +
    df_fact['special_char_range'].fillna('None').astype(str) + '|' +
    df_fact['length_category'].fillna('Unknown').astype(str)
)

print(f"Created keys, nulls remaining: {df_fact['characteristic_key'].isna().sum()}")

# Create composite key in dimension table
df_dim['characteristic_key'] = (
    df_dim['has_ip'].astype(str) + '|' +
    df_dim['has_suspicious_keyword'].astype(str) + '|' +
    df_dim['special_char_range'] + '|' +
    df_dim['length_category']
)

# Save updated files
df_fact.to_csv(fact_path, index=False)
df_dim.to_csv(dim_path, index=False)

print(f"✅ Added characteristic_key to fact_phishing_incident.csv")
print(f"✅ Added characteristic_key to dim_url_characteristics.csv")

# Update SQLite
DB_PATH = Path("data/processed/phishing.db")
conn = sqlite3.connect(DB_PATH)

df_fact.to_sql("fact_phishing_incident", conn, if_exists="replace", index=False)
df_dim.to_sql("dim_url_characteristics", conn, if_exists="replace", index=False)

conn.close()

print(f"\n✅ Updated phishing.db")
print(f"\nSample characteristic keys:")
print(df_fact['characteristic_key'].head(10).tolist())
