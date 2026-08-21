import urllib.request
import json
import re

URL = "https://www.fantacalcio.it/quotazioni-fantacalcio"

def fetch_players():
    req = urllib.request.Request(
        URL, 
        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    )
    
    try:
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            
            # Estrazione o Parsing dei dati della tabella quotazioni
            # Cerchiamo le righe dei giocatori HTML o JSON inline
            players = []
            
            # Regex per intercettare i dati dei calciatori dalla tabella renderizzata
            pattern = re.compile(
                r'data-name="([^"]+)".*?data-team="([^"]+)".*?data-role="([^"]+)".*?data-fvm="([^"]+)"', 
                re.DOTALL
            )
            
            matches = pattern.findall(html)
            
            if not matches:
                # Fallback API / JSON interno Fantacalcio
                json_match = re.search(r'var playerList = (\[.*?\]);', html)
                if json_match:
                    raw_data = json.loads(json_match.group(1))
                    for idx, p in enumerate(raw_data):
                        players.append({
                            "id": idx + 1,
                            "nome": p.get("nome", "Sconosciuto"),
                            "squadra": p.get("squadra", "SERIE A")[:3].upper(),
                            "ruolo": p.get("ruolo", "C").upper(),
                            "fantamedia": float(p.get("fm", 6.0)),
                            "titolarita": int(p.get("tit", 80)),
                            "pma": int(p.get("fvm", 10))
                        })
                    return players

            for idx, m in enumerate(matches):
                players.append({
                    "id": idx + 1,
                    "nome": m[0].strip(),
                    "squadra": m[1].strip()[:3].upper(),
                    "ruolo": m[2].strip().upper(),
                    "fantamedia": 6.5,
                    "titolarita": 85,
                    "pma": int(m[3]) if m[3].isdigit() else 10
                })
                
            return players
    except Exception as e:
        print(f"Errore durante lo scraping: {e}")
        return []

if __name__ == "__main__":
    player_data = fetch_players()
    if len(player_data) > 50:
        with open("players.json", "w", encoding="utf-8") as f:
            json.dump(player_data, f, ensure_ascii=False, indent=2)
        print(f"Aggiornamento completato con successo: {len(player_data)} calciatori salvati.")
    else:
        print("Attenzione: recuperati pochi giocatori. Controlla il selettore.")
