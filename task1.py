from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)

DB_FILE = "data.db" 

@app.route('/')
def index():
    return render_template('file1.html')

@app.route('/submit', methods=['POST'])
def submit():
    
    file = request.files.get('file') 
    if file:
        raw_content = file.read()  
        try:
            
            csvContent = raw_content.decode('utf-8')  
        except UnicodeDecodeError:
            return "File encoding not supported. Please upload a UTF-8 encoded CSV file.", 400

        if csvContent.startswith('\ufeff'):  
            csvContent = csvContent[1:]

        csvArray = csvContent.splitlines()  
        headers = [header.strip() for header in csvArray[0].split(',')]  
        rows = [line.split(',') for line in csvArray[1:]] 

        try:
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()

            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()

            matching_table = None
            for table in tables:
                table_name = table[0]
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = cursor.fetchall()
                existing_headers = [column[1] for column in columns]
                if sorted(headers) == sorted(existing_headers):
                    matching_table = table_name
                    break

            if matching_table:
                
                for row in rows:
                    placeholders = ', '.join(['?'] * len(row))
                    insert_query = f"INSERT INTO {matching_table} VALUES ({placeholders})"
                    cursor.execute(insert_query, row)
                
                select_query = f"SELECT * FROM {matching_table}"
                cursor.execute(select_query)
                data = cursor.fetchall()
                conn.commit()

                return f"Table matches. Data inserted: {data}"
            else:
               
                table_name = "uploaded_data"  
                sanitized_headers = [header.replace(" ", "_") for header in headers]

                cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

                create_table_query = f"CREATE TABLE {table_name} ({', '.join(f'{header} TEXT' for header in sanitized_headers)})"
                cursor.execute(create_table_query)

                for row in rows:
                    placeholders = ', '.join(['?'] * len(row))
                    insert_query = f"INSERT INTO {table_name} VALUES ({placeholders})"
                    cursor.execute(insert_query, row)
                
                select_query = f"SELECT * FROM {table_name}"
                cursor.execute(select_query)
                data = cursor.fetchall()
                conn.commit()

                return f"File processed and saved. Data: {data}"

        except sqlite3.DatabaseError as e:
            return f"Database error occurred: {e}", 500
        finally:
        
            conn.close()

    else:
        return "No file uploaded", 400

if __name__ == "__main__":
    app.run(debug=True, port=5001)
