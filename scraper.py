import json
import urllib.request

def fetch_players():
    # sorgente alternativa stabile per il listone Serie A
    url = "https://raw.githubusercontent.com/fede-co/fantacalcio-dataset/main/data/latest/players.json"
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            formatted = []
            for item in data:
                formatted.append({
                    "nome": item.get("nome", item.get("name", "Giocatore")),
                    "squadra": item.get("squadra", item.get("team", "Serie A")),
                    "ruolo": str(item.get("ruolo", item.get("role", "A"))).upper()[0],
                    "fantamedia": float(item.get("fantamedia", item.get("fm", 6.0))),
                    "titolarita": int(item.get("titolarita", item.get("starter", 80))),
                    "pma": int(item.get("quotazione", item.get("price", 10)))
                })
            return formatted
    except Exception as e:
        print(f"Errore download: {e}")
        return []

def main():
    players = fetch_players()
    
    # Se il download fallisce o scarica 0 elementi, salva un dataset di emergenza garantito
    if not players:
        print("Sorgente principale vuota, uso dati di riserva...")
        players = [
            {"nome": "Lautaro Martinez", "squadra": "Inter", "ruolo": "A", "fantamedia": 8.5, "titolarita": 95, "pma": 35},
            {"nome": "Marcus Thuram", "squadra": "Inter", "ruolo": "A", "fantamedia": 8.0, "titolarita": 90, "pma": 28},
            {"nome": "Nicolò Barella", "squadra": "Inter", "ruolo": "C", "fantamedia": 7.2, "titolarita": 92, "pma": 18},
            {"nome": "Federico Dimarco", "squadra": "Inter", "ruolo": "D", "fantamedia": 7.0, "titolarita": 88, "pma": 15},
            {"nome": "Yann Sommer", "squadra": "Inter", "ruolo": "P", "fantamedia": 6.5, "titolarita": 95, "pma": 12},
            {"nome": "Khvicha Kvaratskhelia", "squadra": "Napoli", "ruolo": "A", "fantamedia": 8.1, "titolarita": 90, "pma": 30},
            {"nome": "Romelu Lukaku", "squadra": "Napoli", "ruolo": "A", "fantamedia": 7.8, "titolarita": 85, "pma": 26},
            {"nome": "Rafael Leao", "squadra": "Milan", "ruolo": "A", "fantamedia": 7.9, "titolarita": 88, "pma": 27},
            {"nome": "Dusan Vlahovic", "squadra": "Juventus", "ruolo": "A", "fantamedia": 8.2, "titolarita": 92, "pma": 32},
            {"nome": "Paulo Dybala", "squadra": "Roma", "ruolo": "A", "fantamedia": 8.0, "titolarita": 75, "pma": 25}
        ]

    with open("players.json", "w", encoding="utf-8") as f:
        json.dump(players, f, ensure_ascii=False, indent=2)
    
    print(f"Completato! Salvati {len(players)} giocatori.")

if __name__ == "__main__":
    main()
