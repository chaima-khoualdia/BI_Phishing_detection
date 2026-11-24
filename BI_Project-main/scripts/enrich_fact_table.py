import pandas as pd
import sqlite3
from pathlib import Path

# Load fact table
processed_path = Path("data/processed/fact_phishing_incident.csv")
df = pd.read_csv(processed_path)

print("Enriching fact table with dimension link columns...")

# 1. Add length_category
def categorize_length(length):
    if length < 20:
        return 'Very Short (<20)'
    elif length < 30:
        return 'Short (20-29)'
    elif length < 50:
        return 'Medium (30-49)'
    elif length < 100:
        return 'Long (50-99)'
    else:
        return 'Very Long (100+)'

df['length_category'] = df['length'].apply(categorize_length)
print("✅ Added length_category")

# 2. Add special_char_range
def categorize_special_chars(count):
    if count == 0:
        return 'None'
    elif count <= 3:
        return 'Low (1-3)'
    elif count <= 7:
        return 'Medium (4-7)'
    elif count <= 15:
        return 'High (8-15)'
    else:
        return 'Very High (15+)'

df['special_char_range'] = df['special_char_count'].apply(categorize_special_chars)
print("✅ Added special_char_range")

# Save updated CSV
df.to_csv(processed_path, index=False)
print(f"\n✅ Updated fact_phishing_incident.csv")
print(f"   Columns: {df.columns.tolist()}")

# Update SQLite database
DB_PATH = Path("data/processed/phishing.db")
conn = sqlite3.connect(DB_PATH)
df.to_sql("fact_phishing_incident", conn, if_exists="replace", index=False)
conn.close()

print(f"\n✅ Updated phishing.db")
print(f"\nNew dimension relationships:")
print(f"   - fact.label → dim_label.label_name")
print(f"   - fact.Domain → dim_domain.domain_name")
print(f"   - fact.length_category → dim_url_length.length_category")
print(f"   - fact.(has_ip, has_suspicious_keyword, special_char_range, length_category) → dim_url_characteristics")
