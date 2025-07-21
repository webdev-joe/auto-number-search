# ✅ Step 1: Download ZIP
ZIP_URL = "https://www.thenumberingsystem.com.au/download/EnhancedFullDownload.zip"

import requests
import zipfile
import io
import csv
import json
import os
import pandas as pd

def download_and_extract_csv():
    response = requests.get(ZIP_URL)
    response.raise_for_status()
    print("📦 ZIP file downloaded. Extracting...")

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        for file in z.namelist():
            if file.endswith('.csv'):
                print(f"📝 Found CSV file in ZIP: {file}")
                with z.open(file) as csvfile:
                    return pd.read_csv(csvfile)
    raise Exception("CSV file not found in ZIP.")

def filter_available_numbers(df):
    df = df[df["Status"].str.strip().str.lower() == "spare"].copy()
    df["From"] = pd.to_numeric(df["From"], errors="coerce")
    df["To"] = pd.to_numeric(df["To"], errors="coerce")
    df.dropna(subset=["From", "To"], inplace=True)

    MAX_EXPANSION = 10000
    available_numbers = []

    for _, row in df.iterrows():
        prefix = str(row["Prefix"]).strip()
        start = int(row["From"])
        end = int(row["To"])

        if end - start > MAX_EXPANSION:
            continue

        for number in range(start, end + 1):
            if prefix == "13":
                full_number = f"{prefix}{str(number).zfill(4)}"
            elif prefix in ["1300", "1800"]:
                full_number = f"{prefix}{str(number).zfill(6)}"
            else:
                continue
            available_numbers.append({"number": full_number})

    print(f"🔢 Total available numbers collected: {len(available_numbers):,}")
    return available_numbers

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
