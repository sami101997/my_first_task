import sqlite3
import csv

def create_table_and_insert_data(csv_file, db_file):
    """
    Reads a CSV file and inserts its content into a table in an SQLite database.
    
    Parameters:
        csv_file (str): Path to the CSV file.
        db_file (str): Path to the SQLite database file.
    """
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()

        # Open the CSV file
        with open(csv_file, newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            # Get column names from the CSV file
            columns = reader.fieldnames
            
            # Create table if it doesn't exist
            create_table_query = f"CREATE TABLE IF NOT EXISTS Data ({', '.join([f'{col} TEXT' for col in columns])});"
            cursor.execute(create_table_query)
            
            # Insert rows into the table
            for row in reader:
                placeholders = ', '.join(['?' for _ in columns])
                insert_query = f"INSERT INTO Data ({', '.join(columns)}) VALUES ({placeholders});"
                cursor.execute(insert_query, tuple(row[col] for col in columns))
        
        # Commit changes and close the connection
        conn.commit()
        print(f"Data successfully inserted into the database: {db_file}")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()


