import requests
import json
import os

# URL dell'API / File JSON o Excel delle quotazioni aggiornate
URL_QUOTAZIONI = "https://www.fantacalcio.it/api/v1/Quotazioni/GetQuotazioni"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://www.fantacalcio.it/quotazioni-fantacalcio"
}

def clean_role(role_raw):
    r = str(role_raw).upper().strip()
    if 'POR' in r or r == 'P': return 'P'
    if 'DIF' in r or r == 'D': return 'D'
    if 'CEN' in r or r == 'C': return 'C'
    if 'ATT' in r or r == 'A': return 'A'
    return 'C'

def main():
    print("Inizio scaricamento listone...")
    
    players = []
    
    try:
        response = requests.get(URL_QUOTAZIONI, headers=headers, timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            # Se l'API restituisce i dati sotto forma di lista
            raw_list = data if isinstance(data, list) else data.get("data", [])
            
            for idx, p in enumerate(raw_list):
                players.append({
                    "id": idx + 1,
                    "nome": p.get("Nome") or p.get("nome") or "Calciatore",
                    "squadra": (p.get("Squadra") or p.get("squadra") or "SERIE A")[:3].upper(),
                    "ruolo": clean_role(p.get("Ruolo") or p.get("ruolo") or "C"),
                    "fantamedia": float(p.get("Fantamedia") or p.get("fm") or 6.0),
                    "titolarita": int(p.get("Titolarita") or p.get("tit") or 85),
                    "pma": int(p.get("QtA") or p.get("fvm") or p.get("pma") or 10)
                })
        else:
            print(f"Chiamata API fallita con codice {response.status_code}, attivazione fallback...")
    except Exception as e:
        print(f"Errore connessione: {e}")

    # Fallback sicuro: Se l'API di Fantacalcio risponde male da GitHub Actions
    if len(players) < 50:
        print("Uso fonte alternativa di emergenza per evitare fallimento workflow...")
        try:
            # Fonte open-data Fantacalcio di riserva
            fallback_url = "https://raw.githubusercontent.com/fanta-data/serie-a-dataset/main/2026/players.json"
            fb_res = requests.get(fallback_url, timeout=10)
            if fb_res.status_code == 200:
                players = fb_res.json()
        except Exception as fb_err:
            print(f"Fallback fallito: {fb_err}")

    # Se abbiamo dati valida, scriviamo il file
    if len(players) > 0:
        with open("players.json", "w", encoding="utf-8") as f:
            json.dump(players, f, ensure_ascii=False, indent=2)
        print(f"OK! Salvati {len(players)} calciatori in players.json")
    else:
        print("Impossibile recuperare i calciatori. Mantengo il file esistente per evitare sovrascritture vuote.")

if __name__ == "__main__":
    main()
