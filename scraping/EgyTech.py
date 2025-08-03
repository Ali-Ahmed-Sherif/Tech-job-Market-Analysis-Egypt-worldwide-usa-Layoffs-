import requests
import pandas as pd
import time
import csv
import os
from itertools import product

# === CONFIGURATION ===
year = 2024  # Confirmed only year supported
filename = f"egytech_tech_jobs_{year}_final2.csv"
log_filename = f"request_stats.csv"
endpoint = "https://api.egytech.fyi/participants"
headers = {"User-Agent": "Mozilla/5.0"}

# === Filters === (Simplified)
titles = [
    "testing", "data_engineer", "ai_automation", "devops_sre_platform", "data_scientist",
    "data_analytics", "embedded", "hardware", "technical_support", "ui_ux", 
    "backend", "frontend", "fullstack"
]
levels = ["junior", "mid_level", "senior", "lead", "director", "intern"]
markets = ["local", "regional", "global"]
sizes = ["small", "medium", "large"]

# === Initialize output CSV ===
if not os.path.exists(filename):
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        pass  # File created

# === Track previously written rows by Timestamp ===
written_rows = set()
try:
    existing_df = pd.read_csv(filename)
    if 'Timestamp' in existing_df.columns:
        written_rows = set(existing_df['Timestamp'])
except Exception:
    pass

# === Log to track request outcomes ===
log_data = []

# === Begin Scraping ===
total_written = 0

for title, level, market, size in product(titles, levels, markets, sizes):
    params = {
        "title": title,
        "level": level,
        "business_market": market,
        "business_size": size,
        "include_remote_abroad": "true",
        "include_relocated": "true"
    }

    try:
        res = requests.get(endpoint, params=params, headers=headers)
        if res.status_code == 200:
            data = res.json().get("results", [])
            count = len(data)
            log_data.append({
                "title": title,
                "level": level,
                "market": market,
                "size": size,
                "count": count
            })

            if not data:
                print(f"⚠️ Empty for {params}")
                continue

            with open(filename, mode='a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                if os.stat(filename).st_size == 0:
                    writer.writeheader()

                new_rows = 0
                for row in data:
                    row_id = row.get("Timestamp")
                    if row_id not in written_rows:
                        writer.writerow(row)
                        written_rows.add(row_id)
                        new_rows += 1

                print(f"✅ {new_rows} new rows written for title={title}, level={level}")
                total_written += new_rows
        else:
            print(f"❌ HTTP {res.status_code} for {params}")

        time.sleep(1.2)

    except Exception as e:
        print(f"❌ Exception: {e}")

# === Save request log ===
pd.DataFrame(log_data).to_csv(log_filename, index=False)
print(f"\n✅ Done: Total rows added in this run = {total_written}")
print(f"📝 Request summary saved to {log_filename}")