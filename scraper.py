import json
import requests
from bs4 import BeautifulSoup

def fetch_fantapazz_players():
    url = "https://www.fantapazz.com/fantacalcio/listone-e-quotazioni"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    formatted_players = []

    try:
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Selezione delle righe del listone FantaPazz
        rows = soup.find_all('tr', class_=['player-row', 'row-player']) or soup.select('table tbody tr')

        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 4:
                continue

            # Estrazione valori dalle colonne della tabella
            nome_el = row.select_one('.name, .player-name, a')
            nome = nome_el.get_text(strip=True) if nome_el else "Calciatore"

            squadra_el = row.select_one('.team, .squadra')
            squadra = squadra_el.get_text(strip=True) if squadra_el else "Serie A"

            ruolo_el = row.select_one('.role, .ruolo')
            ruolo_raw = ruolo_el.get_text(strip=True).upper() if ruolo_el else "A"
            ruolo = ruolo_raw[0] if ruolo_raw else "A"

            quotazione_el = row.select_one('.price, .quotazione, .qt')
            try:
                pma = int(quotazione_el.get_text(strip=True)) if quotazione_el else 10
            except ValueError:
                pma = 10

            formatted_players.append({
                "nome": nome,
                "squadra": squadra,
                "ruolo": ruolo,
                "fantamedia": 6.5,  # Valore stimato di base se non presente in tabella
                "titolarita": 85,
                "pma": pma
            })

    except Exception as e:
        print(f"Errore durante lo scraping da FantaPazz: {e}")

    return formatted_players

def main():
    players = fetch_fantapazz_players()
    
    if players:
        with open("players.json", "w", encoding="utf-8") as f:
            json.dump(players, f, ensure_ascii=False, indent=2)
        print(f"OK: Estratti e salvati {len(players)} giocatori da FantaPazz.")
    else:
        print("Nessun giocatore estratto. Verificare la struttura HTML di FantaPazz.")

if __name__ == "__main__":
    main()
