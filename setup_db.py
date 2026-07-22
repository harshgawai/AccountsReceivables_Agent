import pandas as pd
import sqlite3
import os

DB_PATH = 'data/ar_data.db'

def setup_database():
    if not os.path.exists('data'):
        print("Data directory not found. Please run generate_dataset.py first.")
        return

    print("Connecting to SQLite database...")
    conn = sqlite3.connect(DB_PATH)

    files_to_load = {
        'customers': 'data/customers.csv',
        'invoices': 'data/invoices.csv',
        'communications': 'data/communications.csv'
    }

    for table_name, file_path in files_to_load.items():
        if os.path.exists(file_path):
            print(f"Loading {file_path} into table '{table_name}'...")
            df = pd.read_csv(file_path)
            
            # Write dataframe to sql table
            df.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"Successfully loaded {len(df)} records into '{table_name}'.")
        else:
            print(f"Warning: {file_path} not found. Skipping.")

    # Create some indexes to help the SQL agent with queries
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_invoices_customer ON invoices(customer_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_comms_invoice ON communications(invoice_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_comms_customer ON communications(customer_id)")
    conn.commit()

    conn.close()
    print(f"Database setup complete! SQLite DB saved to {DB_PATH}")

if __name__ == "__main__":
    setup_database()
