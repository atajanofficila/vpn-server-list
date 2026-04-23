import requests
import json
import csv
from collections import defaultdict

URL = "http://www.vpngate.net/api/iphone/"
OUTPUT = "servers.json"

MAX_SERVERS = 120
MAX_PER_COUNTRY = 5
MAX_PING = 350
MIN_SPEED = 300000

def fetch_data():
    r = requests.get(URL, timeout=25)
    r.raise_for_status()
    return r.text

def parse_servers(raw):
    lines = raw.splitlines()

    start = 0
    for i, line in enumerate(lines):
        if line.startswith("#HostName"):
            start = i
            break

    reader = csv.DictReader(lines[start:])
    servers = []

    for row in reader:
        try:
            config = row.get("OpenVPN_ConfigData_Base64", "").strip()
            if not config:
                continue

            ping = int(row.get("Ping", "9999") or 9999)
            speed = int(row.get("Speed", "0") or 0)

            if ping > MAX_PING:
                continue

            if speed < MIN_SPEED:
                continue

            country = row.get("CountryLong", "Unknown").strip()
            ip = row.get("IP", "").strip()

            if not ip:
                continue

            server = {
                "country": country,
                "ip": ip,
                "ping": ping,
                "speed": speed,
                "score": int(row.get("Score", "0") or 0),
                "config": config
            }

            servers.append(server)

        except:
            continue

    return servers

def remove_duplicates(servers):
    seen = set()
    clean = []

    for s in servers:
        key = (s["ip"], s["country"])
        if key in seen:
            continue
        seen.add(key)
        clean.append(s)

    return clean

def smart_sort(servers):
    return sorted(
        servers,
        key=lambda x: (
            x["ping"],
            -x["speed"],
            -x["score"]
        )
    )

def balance_countries(servers):
    grouped = defaultdict(list)

    for s in servers:
        grouped[s["country"]].append(s)

    final = []

    for country, items in grouped.items():
        items = smart_sort(items)
        final.extend(items[:MAX_PER_COUNTRY])

    final = smart_sort(final)
    return final[:MAX_SERVERS]

def save_json(data):
    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def main():
    print("Fetching VPNGate servers...")
    raw = fetch_data()

    servers = parse_servers(raw)
    print("Parsed:", len(servers))

    servers = remove_duplicates(servers)
    print("Unique:", len(servers))

    servers = balance_countries(servers)

    save_json(servers)
    print("Saved:", len(servers), "servers ->", OUTPUT)

if __name__ == "__main__":
    main()
