import sqlite3
import pandas as pd
from pathlib import Path

def load_processed_data():
    """Load the processed phishing data from CSV"""
    processed_path = Path("data/processed/fact_phishing_incident.csv")
    return pd.read_csv(processed_path)

def load_dimension_tables():
    """Load all dimension tables from CSV files"""
    processed_folder = Path("data/processed")
    
    dimensions = {}
    dimension_files = {
        'dim_label': 'dim_label.csv',
        'dim_domain': 'dim_domain.csv',
        'dim_url_characteristics': 'dim_url_characteristics.csv',
        'dim_url_length': 'dim_url_length.csv'
    }
    
    for table_name, file_name in dimension_files.items():
        file_path = processed_folder / file_name
        if file_path.exists():
            dimensions[table_name] = pd.read_csv(file_path)
            print(f"   ✅ Loaded {table_name}: {len(dimensions[table_name])} rows")
        else:
            print(f"   ⚠️  {file_name} not found, skipping {table_name}")
    
    return dimensions

def load_to_sqlite(df, dimensions):
    """Load fact table and dimension tables into SQLite database"""
    DB_PATH = Path("data/processed/phishing.db")
    conn = sqlite3.connect(DB_PATH)

    # Load fact table
    df.to_sql("fact_phishing_incident", conn, if_exists="replace", index=False)
    print(f"   - fact_phishing_incident: {len(df)} rows")
    
    # Load dimension tables
    for table_name, dim_df in dimensions.items():
        dim_df.to_sql(table_name, conn, if_exists="replace", index=False)
        print(f"   - {table_name}: {len(dim_df)} rows")

    conn.close()
    print(f"\n✅ All data loaded into SQLite at {DB_PATH}")

if __name__ == "__main__":
    print("Loading processed data...")
    df = load_processed_data()
    
    print("\nLoading dimension tables...")
    dimensions = load_dimension_tables()
    
    print("\nLoading to SQLite database...")
    load_to_sqlite(df, dimensions)
    
    print("\n=== Database Summary ===")
    print(f"Total phishing incidents: {(df['is_phishing'] == 1).sum()}")
    print(f"Total benign incidents: {(df['is_phishing'] == 0).sum()}")
    print(f"Dimension tables loaded: {len(dimensions)}")
    print(f"Total benign incidents: {(df['is_phishing'] == 0).sum()}")
