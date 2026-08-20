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

        # 1. Cerca dati dentro i tag script JSON
        script_data = soup.find('script', id='__NEXT_DATA__') or soup.find('script', type='application/json')
        
        if script_data:
            json_content = json.loads(script_data.string)
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

        # 2. Parsing tabelle HTML se il JSON fallisce
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

    # Fallback se FantaPazz restituisce 0 giocatori o viene bloccato
    if len(players) < 10:
        print("FantaPazz non accessibile. Caricamento dati Serie A di emergenza...")
        try:
            fallback_url = "https://raw.githubusercontent.com/fede-co/fantacalcio-dataset/main/data/latest/players.json"
            res = requests.get(fallback_url, timeout=10)
            data = res.json()
            
            players = []
            for p in data:
                # Correzione del mapping: 'squadra' nel dataset sorgente è il nome del calciatore
                nome_calciatore = p.get("squadra", p.get("nome", "Giocatore"))
                
                # Se 'nome' è il ruolo (es. P, D, C, A), usiamolo, altrimenti gestiamo i codici
                ruolo_raw = str(p.get("nome", "A")).upper()
                ruolo = ruolo_raw[0] if ruolo_raw in ["P", "D", "C", "A"] else "A"

                players.append({
                    "nome": nome_calciatore,
                    "squadra": p.get("team", "Serie A"),
                    "ruolo": ruolo,
                    "fantamedia": float(p.get("fantamedia", 6.5)),
                    "titolarita": int(p.get("titolarita", 85)),
                    "pma": int(p.get("pma", p.get("quotazione", 10)))
                })
        except Exception as e:
            print(f"Errore fallback: {e}")

    # Salva il file
    if players:
        with open("players.json", "w", encoding="utf-8") as f:
            json.dump(players, f, ensure_ascii=False, indent=2)
        print(f"OK! Salvati {len(players)} giocatori in players.json.")

if __name__ == "__main__":
    main()
