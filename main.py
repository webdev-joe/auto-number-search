import requests
import zipfile
import io
import csv
import json
import os

ZIP_URL = "https://www.thenumberingsystem.com.au/download/EnhancedFullDownload.zip"

def download_and_extract_csv():
    response = requests.get(ZIP_URL)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        for file in z.namelist():
            if file.endswith('.csv'):
                with z.open(file) as csvfile:
                    return csvfile.read().decode('utf-8')
    raise Exception("CSV file not found in ZIP.")

def filter_available_numbers(csv_text):
    reader = csv.DictReader(io.StringIO(csv_text))
    print(f"📋 CSV Headers: {reader.fieldnames}")
    available = []

    for row in reader:
        status = row.get("Status", "").strip().lower()
        from_number = row.get("From", "").strip()
        to_number = row.get("To", "").strip()

        if status != "allocated":
            if from_number.startswith("13") and len(from_number) == 6:
                available.append({"from": from_number, "to": to_number, "status": "available"})
            elif from_number.startswith("1300") and len(from_number) == 10:
                available.append({"from": from_number, "to": to_number, "status": "available"})
            elif from_number.startswith("1800") and len(from_number) == 10:
                available.append({"from": from_number, "to": to_number, "status": "available"})

    print(f"🔢 Found {len(available)} available numbers.")
    return available

def save_to_json(data):
    os.makedirs("docs", exist_ok=True)
    with open("docs/available_numbers.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Saved {len(data)} available numbers to docs/available_numbers.json")

if __name__ == "__main__":
    try:
        print("📥 Downloading ZIP file...")
        csv_text = download_and_extract_csv()
        print("🔍 Filtering available numbers...")
        available = filter_available_numbers(csv_text)
        save_to_json(available)
    except Exception as e:
        print(f"❌ Error: {e}")
