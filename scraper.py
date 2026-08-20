import json
import urllib.request

def fetch_data():
    url = "https://raw.githubusercontent.com/statmilk/fantacalcio-api/main/data/players.json"
    formatted_players = []
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            for item in data:
                formatted_players.append({
                    "nome": item.get("nome", item.get("name", "")),
                    "squadra": item.get("squadra", item.get("team", "")),
                    "ruolo": str(item.get("ruolo", item.get("role", "A"))).upper()[0],
                    "fantamedia": float(item.get("fantamedia", item.get("fm", 6.0))),
                    "titolarita": int(item.get("titolarita", item.get("starter", 80))),
                    "pma": int(item.get("quotazione", item.get("price", 10)))
                })
    except Exception as e:
        print(f"Errore download: {e}")
    return formatted_players

def main():
    players = fetch_data()
    if players:
        with open("players.json", "w", encoding="utf-8") as f:
            json.dump(players, f, ensure_ascii=False, indent=2)
        print(f"Salvati {len(players)} giocatori.")

if __name__ == "__main__":
    main()
