import requests
import zipfile
import io
import csv
import json
import os

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
                    csv_content = csvfile.read().decode('utf-8')
                    print(f"📋 First 300 characters of CSV:\n{csv_content[:300]}")
                    return csv_content

    raise Exception("CSV file not found in ZIP.")

# ✅ Step 2: Filter available numbers
def filter_available_numbers(csv_text):
    reader = csv.DictReader(io.StringIO(csv_text))
    available = []
    headers = reader.fieldnames
    print(f"📋 CSV Headers: {headers}")

    for row in reader:
        number = row.get("From", "").strip()  # Updated based on your CSV structure
        status = row.get("Status", "").strip().lower()

        if status != "allocated":
            if number.startswith("13") and len(number) == 6:
                available.append({"number": number, "status": "available"})
            elif number.startswith("1300") and len(number) == 10:
                available.append({"number": number, "status": "available"})
            elif number.startswith("1800") and len(number) == 10:
                available.append({"number": number, "status": "available"})

    print(f"🔢 Found {len(available)} available numbers.")
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
        csv_text = download_and_extract_csv()
        print("🔍 Filtering available numbers...")
        available = filter_available_numbers(csv_text)
        save_to_json(available)
    except Exception as e:
        print(f"❌ Error: {e}")
