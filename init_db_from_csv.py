import sqlite3
from pathlib import Path

import pandas as pd
from config import DB_PATH

CSV_DIR = Path(__file__).parent / "data" / "csv"

def create_system_db_from_csv():
    # Remove existing DB if you want a clean build each time
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)

    try:
        for csv_file in CSV_DIR.glob("*.csv"):
            table_name = csv_file.stem
            print(f"Loading {csv_file.name} into table '{table_name}'")

            try:
                df = pd.read_csv(csv_file)
            except pd.errors.EmptyDataError:
                print(f"  -> SKIPPED (file is empty: {csv_file.name})")
                continue

            if df.empty or df.columns.size == 0:
                print(f"  -> SKIPPED (no data/columns in: {csv_file.name})")
                continue

            # Write to SQLite; let pandas infer types
            df.to_sql(table_name, conn, if_exists="replace", index=False)

        print(f"\nCreated SQLite DB at: {DB_PATH}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_system_db_from_csv()