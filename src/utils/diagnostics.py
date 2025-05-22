import os
import csv

def initialize_diagnostics_file(output_path, headers):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)

def append_diagnostics_row(output_path, row_data):
    with open(output_path, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(row_data)
