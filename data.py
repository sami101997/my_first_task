from csv import DictReader
from typing import List, Dict


with open("file1.csv", 'r', encoding="utf8") as file_handle:
    csv_reader = DictReader(file_handle)
    table: List[Dict[str, float]] = []
  
    for row in csv_reader:
        float_row: Dict[str, float] = {}
        for column in row:
            value = row[column]
            try:
               
                float_row[column] = float(value)
            except ValueError:
                
                print(f"{column}': {value}")
                float_row[column] = None 
        table.append(float_row)
