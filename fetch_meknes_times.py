#!/usr/bin/env python3
"""
fetch_meknes_times.py
Fetch prayer times for Meknes, Morocco from AlAdhan API and save to CSV with Arabic headers.

Usage:
    python fetch_meknes_times.py --year 2025
    python fetch_meknes_times.py --year 2024 2025   # multiple years
    python fetch_meknes_times.py       # defaults to current year

Outputs:
    meknes_prayer_times_<year>.csv
CSV columns (Arabic):
    تاريخ,الفجر,الظهر,العصر,المغرب,العشاء,place
"""

import requests
import csv
import datetime
import argparse
import time
import os

API_URL = "https://api.aladhan.com/v1/calendarByCity"
CITY = "Meknes"
COUNTRY = "Morocco"
# method can be adjusted (1=University of Islamic Sciences, Karachi, 2=...); choose 2 or leave default
METHOD = 2
PLACE_NAME = "مدينة مكناس - المغرب"

def clean_time(t):
    """
    AlAdhan sometimes returns times like '05:12 (CEST)' or '05:12'. We want HH:MM.
    """
    if not t:
        return ""
    t = t.strip()
    # take first 5 chars that look like HH:MM
    # find first occurrence of pattern digit digit : digit digit
    import re
    m = re.search(r"(\d{1,2}:\d{2})", t)
    if m:
        hhmm = m.group(1)
        # normalize to 2-digit hour
        parts = hhmm.split(":")
        h = int(parts[0])
        mm = parts[1]
        return f"{h:02d}:{mm}"
    return t[:5]

def fetch_month(year, month, city=CITY, country=COUNTRY, method=METHOD):
    """
    Returns list of dicts for each day in the month with keys:
    date (YYYY-MM-DD), Fajr, Dhuhr, Asr, Maghrib, Isha
    """
    params = {
        "city": city,
        "country": country,
        "method": method,
        "month": month,
        "year": year
    }
    resp = requests.get(API_URL, params=params, timeout=15)
    resp.raise_for_status()
    js = resp.json()
    if js.get("code") != 200 or "data" not in js:
        raise RuntimeError("Unexpected API response: " + str(js))
    results = []
    for item in js["data"]:
        # each item has 'date' and 'timings'
        date_gregorian = item.get("date", {}).get("gregorian", {}).get("date")
        timings = item.get("timings", {})
        # clean times
        fajr = clean_time(timings.get("Fajr", ""))
        dhuhr = clean_time(timings.get("Dhuhr", ""))
        asr = clean_time(timings.get("Asr", ""))
        maghrib = clean_time(timings.get("Maghrib", ""))
        isha = clean_time(timings.get("Isha", ""))
        results.append({
            "date": date_gregorian,  # format DD-MM-YYYY from AlAdhan; we'll convert to YYYY-MM-DD
            "Fajr": fajr,
            "Dhuhr": dhuhr,
            "Asr": asr,
            "Maghrib": maghrib,
            "Isha": isha
        })
    return results

def to_iso_date(d_greg):
    # AlAdhan returns date like '16-10-2025' (DD-MM-YYYY). Convert to YYYY-MM-DD
    try:
        parts = d_greg.split("-")
        if len(parts) == 3:
            dd, mm, yyyy = parts
            return f"{yyyy}-{int(mm):02d}-{int(dd):02d}"
    except:
        pass
    return d_greg

def fetch_year(year, out_dir=".", city=CITY, country=COUNTRY, method=METHOD, place=PLACE_NAME, delay_between_calls=1.0):
    all_days = {}
    for month in range(1, 13):
        print(f"Fetching {year}-{month:02d} ...")
        try:
            month_data = fetch_month(year, month, city=city, country=country, method=method)
        except Exception as e:
            print("  Error fetching month:", e)
            print("  Retrying after 2s...")
            time.sleep(2)
            month_data = fetch_month(year, month, city=city, country=country, method=method)
        for item in month_data:
            iso = to_iso_date(item["date"])
            all_days[iso] = {
                "Fajr": item["Fajr"],
                "Dhuhr": item["Dhuhr"],
                "Asr": item["Asr"],
                "Maghrib": item["Maghrib"],
                "Isha": item["Isha"]
            }
        time.sleep(delay_between_calls)  # be polite
    # write CSV with Arabic headers
    fname = os.path.join(out_dir, f"meknes_prayer_times_{year}.csv")
    headers_ar = ["تاريخ","الفجر","الظهر","العصر","المغرب","العشاء","place"]
    with open(fname, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers_ar)
        for date in sorted(all_days.keys()):
            row = [
                date,
                all_days[date].get("Fajr",""),
                all_days[date].get("Dhuhr",""),
                all_days[date].get("Asr",""),
                all_days[date].get("Maghrib",""),
                all_days[date].get("Isha",""),
                place
            ]
            writer.writerow(row)
    print("Saved:", fname)
    return fname

def main():
    parser = argparse.ArgumentParser(description="Fetch Meknes prayer times and save CSV (Arabic headers).")
    parser.add_argument("--year", nargs="+", type=int, help="One or more years to fetch (e.g. 2025). Defaults to current year.")
    parser.add_argument("--out", type=str, default=".", help="Output directory (default current).")
    args = parser.parse_args()
    years = args.year or [datetime.date.today().year]
    for y in years:
        fetch_year(y, out_dir=args.out)

if __name__ == "__main__":
    main()
