import pandas as pd
import json
import os
from collections import defaultdict

file_path = 'Sample Routine .xlsx'

# Get all sheet names
excel_file = pd.ExcelFile(file_path)
sheet_names = excel_file.sheet_names

print(f"Found {len(sheet_names)} sheets: {sheet_names}\n")

# Parse each sheet
clients = []
client_id = 1

for sheet_name in sheet_names:
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    
    print(f"Processing sheet: {sheet_name}")
    print(f"Shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
    print(f"First few rows:")
    print(df.head(10))
    print("\n" + "="*80 + "\n")

print("\nDone!")
