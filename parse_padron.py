import csv
import json
from datetime import datetime

def process_padron_file(input_file, output_file):
    data = []

    # Try different encodings
    encodings = ['utf-8', 'iso-8859-1', 'latin1']
    
    for encoding in encodings:
        try:
            with open(input_file, 'r', encoding=encoding) as file:
                csv_reader = csv.reader(file)
                for row in csv_reader:
                    if len(row) >= 8:
                        data.append({
                            'id_number': row[0],
                            'first_name': row[5].strip(),
                            'lastname1': row[6].strip(),
                            'lastname2': row[7].strip()
                        })
            break  # If successful, break the loop
        except UnicodeDecodeError:
            continue  # If unsuccessful, try the next encoding
    else:
        raise ValueError(f"Unable to decode the file with any of the encodings: {encodings}")

    with open(output_file, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    input_file = 'PADRON_COMPLETO.txt'  # Replace with your input file name
    current_date = datetime.now().strftime('%Y%m%d')
    output_file = f'cr_padron_{current_date}.json'

    process_padron_file(input_file, output_file)
    print(f"Processing complete. Output saved to {output_file}")