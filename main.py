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

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        for file in z.namelist():
            if file.endswith('.csv'):
                with z.open(file) as csvfile:
                    return csvfile.read().decode('utf-8')
    raise Exception("CSV file not found in ZIP.")

# ✅ Step 2: Filter available numbers
def filter_available_numbers(csv_text):
    reader = csv.DictReader(io.StringIO(csv_text))
    available = []

    for row in reader:
        status = row.get("Status", "").strip().lower()
        from_num = row.get("From", "").strip()
        to_num = row.get("To", "").strip()

        # Skip if allocated or missing
        if status == "allocated" or not from_num.isdigit() or not to_num.isdigit():
            continue

        # Expand number range
        for num in range(int(from_num), int(to_num) + 1):
            str_num = str(num)
            if (str_num.startswith("13") and len(str_num) == 6) or \
               (str_num.startswith("1300") and len(str_num) == 10) or \
               (str_num.startswith("1800") and len(str_num) == 10):
                available.append({"number": str_num, "status": "available"})

    print(f"🔢 Found {len(available)} available numbers.")
    return available

# ✅ Step 3: Save JSON to /docs
def save_to_json(data):
    os.makedirs("docs", exist_ok=True)
    with open("docs/available_numbers.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Saved {len(data)} available numbers to docs/available_numbers.json")

# 🔁 Run everything
if __name__ == "__main__":
    try:
        print("📥 Downloading ZIP file...")
        csv_text = download_and_extract_csv()
        print("🔍 Filtering available numbers...")
        available = filter_available_numbers(csv_text)
        save_to_json(available)
    except Exception as e:
        print(f"❌ Error: {e}")
