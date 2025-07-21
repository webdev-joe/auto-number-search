import requests
import zipfile
import io
import csv
import json
import os
import pandas as pd

# ✅ Step 1: Download ZIP
ZIP_URL = "https://www.thenumberingsystem.com.au/download/EnhancedFullDownload.zip"

def download_and_extract_csv():
    response = requests.get(ZIP_URL)
    response.raise_for_status()
    print("📦 ZIP file downloaded. Extracting...")

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        for file in z.namelist():
            if file.endswith('.csv'):
                print(f"📝 Found CSV file in ZIP: {file}")
                with z.open(file) as csvfile:
                    return pd.read_csv(csvfile)  # ✅ returns a DataFrame

    raise Exception("CSV file not found in ZIP.")

# ✅ Step 2: Filter available numbers from DataFrame
def filter_available_numbers(df):
    available = []
    print(f"📋 DataFrame Columns: {df.columns.tolist()}")

    # ✅ DIAGNOSTIC: Show sample non-empty EROU holders
    non_empty_erou_samples = df[
        df["Current EROU holder"].notna() & (df["Current EROU holder"].str.strip() != "")
    ]["Current EROU holder"].head(10)
    print("🔍 Sample non-empty EROU holders:", non_empty_erou_samples.tolist())

    # ✅ DIAGNOSTIC: Count rows that are 'spare' and have empty EROU
    spare_and_empty_erou = df[
        (df["Status"].str.strip().str.lower() == "spare") &
        (df["Current EROU holder"].isna() | (df["Current EROU holder"].str.strip() == ""))
    ]
    print(f"🔢 Spare with truly empty EROU: {len(spare_and_empty_erou)} rows")

    count = 0
    match_count_13 = 0
    match_count_1300 = 0
    match_count_1800 = 0

    for _, row in df.iterrows():
        status = str(row.get("Status", "")).strip().lower()
        erou_holder = str(row.get("Current EROU holder", "")).strip()
        from_number = str(row.get("From", "")).strip()
        to_number = str(row.get("To", "")).strip()

        if not from_number.isdigit() or not to_number.isdigit():
            continue

        if status == "spare" and not erou_holder:
            start = int(from_number)
            end = int(to_number)

            for number in range(start, end + 1):
                number_str = str(number)
                if number_str.startswith("13") and len(number_str) == 6:
                    match_count_13 += 1
                elif number_str.startswith("1300") and len(number_str) == 10:
                    match_count_1300 += 1
                elif number_str.startswith("1800") and len(number_str) == 10:
                    match_count_1800 += 1

    print(f"🧪 Spare numbers with no EROU — Matching 13: {match_count_13}, 1300: {match_count_1300}, 1800: {match_count_1800}")
    return available



# ✅ Step 3: Save to /docs
def save_to_json(data):
    os.makedirs("docs", exist_ok=True)
    with open("docs/available_numbers.json", "w") as f:
        json.dump(data, f, indent=2)
    print("✅ JSON file saved at docs/available_numbers.json")

# 🔁 Run
if __name__ == "__main__":
    try:
        print("📥 Downloading ZIP file...")
        df = download_and_extract_csv()
        print("🔍 Filtering available numbers...")
        available = filter_available_numbers(df)
        save_to_json(available)
    except Exception as e:
        print(f"❌ Error: {e}")
