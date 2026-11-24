from pathlib import Path

import mysql.connector
import pandas as pd

# MySQL connection configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # Update with your MySQL username
    'password': '23092004C',  # Update with your MySQL password
    'database': 'bi-project'  # Update with your database name
}

# Output directory
OUTPUT_DIR = Path("data/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def export_dimension_tables():
    """Export all dimension tables from MySQL to CSV"""
    
    print("Connecting to MySQL database...")
    # Connect without database first, then select it
    conn = mysql.connector.connect(
        host=DB_CONFIG['host'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password']
    )
    cursor = conn.cursor()
    cursor.execute("USE `bi-project`")
    cursor.close()
    
    # List of dimension tables to export
    dimension_tables = [
        'dim_label',
        'dim_domain',
        'dim_url_characteristics',
        'dim_url_length'
    ]
    
    print(f"\nExporting dimension tables to {OUTPUT_DIR.absolute()}...\n")
    
    for table_name in dimension_tables:
        try:
            # Query the dimension table
            query = f"SELECT * FROM {table_name}"
            df = pd.read_sql(query, conn)
            
            # Save to CSV
            output_path = OUTPUT_DIR / f"{table_name}.csv"
            df.to_csv(output_path, index=False)
            
            print(f"✅ {table_name}: {len(df)} rows exported to {table_name}.csv")
            
        except Exception as e:
            print(f"❌ Error exporting {table_name}: {e}")
    
    conn.close()
    print("\n✅ All dimension tables exported successfully!")

if __name__ == "__main__":
    export_dimension_tables()
