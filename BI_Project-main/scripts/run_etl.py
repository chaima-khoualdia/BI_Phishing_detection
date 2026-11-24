from pathlib import Path
import pandas as pd

from transform.transform import transform_dataset
from load.load import save_outputs, load_to_sqlite   # add DB loader

def main():
    # Step 1: Extract
    print("\n--- Extract ---")
    csv_path = Path("data/raw/urls.csv")
    df_raw = pd.read_csv(csv_path)
    print(df_raw.head())

    # Step 2: Transform
    print("\n--- Transform ---")
    df = transform_dataset(df_raw)
    print(df.head())

    # Step 3: Aggregations
    print("\n--- Aggregations ---")
    incidents_per_period = (
        df.groupby("period_ym")["is_phishing"]
          .agg(total_urls="count", phishing_incidents="sum")
          .reset_index()
    )
    incidents_per_period["phishing_rate"] = (
        incidents_per_period["phishing_incidents"] / incidents_per_period["total_urls"]
    )

    length_stats = (
        df.groupby("is_phishing")["url_length"]
          .agg(avg_url_length="mean", max_url_length="max", min_url_length="min")
          .reset_index()
    )

    print(incidents_per_period.head())
    print(length_stats.head())

    # Step 4: Load (CSV)
    print("\n--- Load (CSV) ---")
    save_outputs(df, incidents_per_period, length_stats)

    # Step 5: Load (SQLite DB)
    print("\n--- Load (SQLite DB) ---")
    load_to_sqlite(df, incidents_per_period, length_stats)

    print("\n✅ ETL pipeline finished successfully!")


if __name__ == "__main__":
    main()
