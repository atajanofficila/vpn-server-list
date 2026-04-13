import requests
import json

URL = "http://www.vpngate.net/api/iphone/"

def fetch_servers():
    res = requests.get(URL, timeout=15)
    lines = res.text.splitlines()

    servers = []

    for line in lines:
        if line.startswith("*") or line.strip() == "":
            continue

        parts = line.split(",")

        if len(parts) < 15:
            continue

        try:
            ping = int(parts[3])
            speed = int(parts[4])

            # filtre
            if ping > 200 or speed < 1000000:
                continue

            server = {
                "ip": parts[1],
                "country": parts[5],
                "ping": ping,
                "speed": speed,
                "config": parts[14]
            }

            servers.append(server)

        except:
            continue

    # en iyi 50 server
    servers = sorted(servers, key=lambda x: x["ping"])[:50]

    return servers


def save_json(data):
    with open("servers.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


if __name__ == "__main__":
    servers = fetch_servers()
    save_json(servers)
