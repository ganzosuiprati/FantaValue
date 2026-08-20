import json
import re
import requests
from bs4 import BeautifulSoup

def fetch_fantapazz():
    url = "https://www.fantapazz.com/fantacalcio/listone-e-quotazioni"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "it-IT,it;q=0.9"
    }

    players = []

    try:
        response = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. Cerca dati dentro i tag script JSON (tipico di Next.js / Nuxt usati da FantaPazz)
        script_data = soup.find('script', id='__NEXT_DATA__') or soup.find('script', type='application/json')
        
        if script_data:
            json_content = json.loads(script_data.string)
            # Ricerca ricorsiva nell'albero JSON per trovare l'array dei giocatori
            def search_json(obj):
                nonlocal players
                if isinstance(obj, dict):
                    if "nome" in obj and ("quotazione" in obj or "pma" in obj or "ruolo" in obj):
                        players.append({
                            "nome": obj.get("nome", obj.get("name", "Giocatore")),
                            "squadra": obj.get("squadra", obj.get("team", "Serie A")),
                            "ruolo": str(obj.get("ruolo", "A")).upper()[0],
                            "fantamedia": float(obj.get("fantamedia", obj.get("fm", 6.5))),
                            "titolarita": int(obj.get("titolarita", 85)),
                            "pma": int(obj.get("quotazione", obj.get("price", 10)))
                        })
                    for v in obj.values():
                        search_json(v)
                elif isinstance(obj, list):
                    for item in obj:
                        search_json(item)

            search_json(json_content)

        # 2. Se l'estrazione JSON fallisce, prova il parsing delle tabelle HTML
        if not players:
            rows = soup.select('table tbody tr')
            for row in rows:
                cols = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
                if len(cols) >= 4:
                    players.append({
                        "nome": cols[0],
                        "squadra": cols[1] if len(cols) > 1 else "Serie A",
                        "ruolo": cols[2][0].upper() if len(cols) > 2 and cols[2] else "A",
                        "fantamedia": 6.5,
                        "titolarita": 85,
                        "pma": int(cols[3]) if cols[3].isdigit() else 10
                    })

    except Exception as e:
        print(f"Errore durante lo scaricamento da FantaPazz: {e}")

    return players

def main():
    players = fetch_fantapazz()

    # Salvagente: Se FantaPazz blocca le richieste o restituisce 0 giocatori, usa il listone Serie A aggiornato
    if len(players) < 10:
        print("FantaPazz non accessibile o protetto da anti-bot. Caricamento dati Serie A di emergenza...")
        try:
            fallback_url = "https://raw.githubusercontent.com/fede-co/fantacalcio-dataset/main/data/latest/players.json"
            res = requests.get(fallback_url, timeout=10)
            data = res.json()
            players = [{
                "nome": p.get("nome", p.get("name", "")),
                "squadra": p.get("squadra", p.get("team", "")),
                "ruolo": str(p.get("ruolo", "A")).upper()[0],
                "fantamedia": float(p.get("fantamedia", 6.0)),
                "titolarita": int(p.get("titolarita", 80)),
                "pma": int(p.get("quotazione", 10))
            } for p in data]
        except Exception as e:
            print(f"Errore fallback: {e}")

    # Salva sempre un file valido
    if players:
        with open("players.json", "w", encoding="utf-8") as f:
            json.dump(players, f, ensure_ascii=False, indent=2)
        print(f"OK! Salvati {len(players)} giocatori in players.json.")

if __name__ == "__main__":
    main()
