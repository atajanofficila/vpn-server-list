import requests
import json

URL = "http://www.vpngate.net/api/iphone/"

def fetch_servers():
    res = requests.get(URL, timeout=20)
    lines = res.text.splitlines()

    servers = []

    for line in lines:
        if line.startswith("*") or line.startswith("#") or line.strip() == "":
            continue

        parts = line.split(",")

        if len(parts) < 15:
            continue

        try:
            ping = int(parts[3] or 9999)
            speed = int(parts[4] or 0)

            config = parts[14].strip()
            if not config:
                continue

            server = {
                "ip": parts[1],
                "country": parts[5],
                "ping": ping,
                "speed": speed,
                "config": config
            }

            servers.append(server)

        except:
            continue

    # sadece sırala
    servers = sorted(servers, key=lambda x: x["ping"])

    return servers


def save_json(data):
    with open("servers.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    servers = fetch_servers()
    save_json(servers)
    print("Saved:", len(servers))
