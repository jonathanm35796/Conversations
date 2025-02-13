import json
import pandas as pd
from pathlib import Path
import numpy as np
from datetime import datetime
import os
class TimestampEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        return super().default(obj)

def process_files(base_dir):
    all_conversations = {}

    base_path = Path(base_dir)
    for file in base_path.rglob("*"):
        try:
            if file.suffix == ".xlsx":
                excel_data = pd.read_excel(file, sheet_name=None)

                file_data = {}
                for sheet_name, df in excel_data.items():
                    sheet_data = df.to_dict(orient='records')
                    file_data[sheet_name] = sheet_data

                all_conversations[str(file)] = file_data
                print(f"Processed Excel file: {file}")

            elif file.suffix == ".csv":
                csv_data = pd.read_csv(file)
                file_data = csv_data.to_dict(orient='records')
                all_conversations[str(file)] = file_data
                print(f"Processed CSV file: {file}")

        except Exception as e:
            print(f"Error processing {file}: {str(e)}")

    return all_conversations

def main():
    base_dir = r"C:\Users\JonathanSMcFarland\Cloud-Drive_jonathan.s.mcfarland@gmail.com\IPhone Export Data\iPhone\Messages"

    print("Starting to process files...")
    conversations = process_files(base_dir)

    output_file = "conversations.json"
    print(f"Writing data to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(conversations, f, indent=2, ensure_ascii=False, cls=TimestampEncoder)

    print("Processing complete!")
    print(f"Output saved to: {os.path.abspath(output_file)}")

if __name__ == "__main__":
    main()