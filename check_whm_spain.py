import os, json, re, sys
import requests
from bs4 import BeautifulSoup

URL = "https://immi.homeaffairs.gov.au/what-we-do/whm-program/status-of-country-caps"
STATE_FILE = "spain_status.json"

def fetch_status() -> str:
    r = requests.get(URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    for tr in soup.select("table tr"):
        tds = [td.get_text(" ", strip=True) for td in tr.select("td")]
        if not tds:
            continue
        if tds[0].strip().lower() == "spain":
            raw = (tds[1] if len(tds) > 1 else "").lower()
            raw = re.sub(r"\s+", " ", raw).strip()
            if "paused" in raw:
                return "PAUSED"
            if "open" in raw:
                return "OPEN"
            if "check ballot status" in raw:
                return "BALLOT"
            return raw.upper() or "UNKNOWN"
    return "NOT_FOUND"

def load_prev():
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f).get("status")

def save(status: str):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"status": status}, f)

def main():
    current = fetch_status()
    prev = load_prev()
    print(f"Prev={prev} Current={current}")

    if prev is None:
        save(current)
        print("Initialized.")
        return 0

    if current != prev:
        save(current)
        print(f"CHANGED {prev} -> {current}")
        return 2

    print("No change.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
