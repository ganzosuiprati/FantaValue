import json
import requests

# Fonti primarie con l'intero listone ufficiale Serie A
SOURCES = [
    # API / Dump Fantacalcio.it & Fantagazzetta completa
    "https://raw.githubusercontent.com/vittorioparis/fantacalcio-dataset/main/data/quotazioni.json",
    # Alternative / Fantaredazione dump
    "https://raw.githubusercontent.com/Stat-FC/fantacalcio-data/main/quotazioni_stats.json",
    "https://raw.githubusercontent.com/fede-co/fantacalcio-api/main/quotazioni.json"
]

TEAM_LOGOS = {
    "ATA": "https://upload.wikimedia.org/wikipedia/it/7/77/Atalanta_BC_logo.svg",
    "BOL": "https://upload.wikimedia.org/wikipedia/it/d/d8/Bologna_FC_1909_logo.svg",
    "CAG": "https://upload.wikimedia.org/wikipedia/it/3/3d/Cagliari_Calcio_2015.svg",
    "COM": "https://upload.wikimedia.org/wikipedia/it/2/29/Como_1907_logo.svg",
    "EMP": "https://upload.wikimedia.org/wikipedia/it/a/a3/Empoli_FC_logo_%282021%29.svg",
    "FIO": "https://upload.wikimedia.org/wikipedia/it/c/c2/ACF_Fiorentina_2022.svg",
    "GEN": "https://upload.wikimedia.org/wikipedia/it/3/37/Genoa_cfc.svg",
    "INT": "https://upload.wikimedia.org/wikipedia/commons/0/05/FC_Internazionale_Milano_2021.svg",
    "JUV": "https://upload.wikimedia.org/wikipedia/commons/b/bc/Juven_logo.png",
    "LAZ": "https://upload.wikimedia.org/wikipedia/it/a/a2/SSLazio_Logo.svg",
    "LEC": "https://upload.wikimedia.org/wikipedia/it/a/a7/US_Lecce_2009.svg",
    "MIL": "https://upload.wikimedia.org/wikipedia/commons/d/d0/Logo_of_AC_Milan.svg",
    "MON": "https://upload.wikimedia.org/wikipedia/it/f/f8/AC_Monza_2021.svg",
    "NAP": "https://upload.wikimedia.org/wikipedia/commons/2/28/SSC_Napoli_2024.svg",
    "PAR": "https://upload.wikimedia.org/wikipedia/it/0/03/Parma_Calcio_1913.svg",
    "ROM": "https://upload.wikimedia.org/wikipedia/it/f/f7/AS_Roma_logo_%282017%29.svg",
    "TOR": "https://upload.wikimedia.org/wikipedia/it/1/1b/Torino_FC_logo.svg",
    "UDI": "https://upload.wikimedia.org/wikipedia/it/3/32/Udinese_Calcio_logo_2010.svg",
    "VER": "https://upload.wikimedia.org/wikipedia/it/9/92/Hellas_Verona_FC_logo_2020.svg",
    "VEN": "https://upload.wikimedia.org/wikipedia/it/e/eb/Venezia_FC_2022.svg"
}

def clean_role(raw_role):
    r = str(raw_role).strip().upper()
    if r in ["P", "POR", "1"]: return "P"
    if r in ["D", "DIF", "2"]: return "D"
    if r in ["C", "CEN", "3"]: return "C"
    return "A"

def update_database():
    print("🔄 Download del listone COMPLETO in corso...")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    players_db = []

    for url in SOURCES:
        try:
            res = requests.get(url, headers=headers, timeout=12)
            if res.status_code == 200:
                data = res.json()
                raw_list = data.get("data", data) if isinstance(data, dict) else data
                
                # Accettiamo il dataset solo se contiene l'intero listone (> 200 giocatori)
                if isinstance(raw_list, list) and len(raw_list) > 200:
                    for idx, p in enumerate(raw_list):
                        nome = p.get("nome") or p.get("Nome") or p.get("name") or p.get("Player")
                        if not nome: continue
                        
                        squadra = str(p.get("squadra") or p.get("Squadra") or p.get("Team") or "SER")[:3].upper()
                        ruolo = clean_role(p.get("ruolo") or p.get("R") or p.get("Role") or "A")
                        
                        # Quotazione / PMA
                        pma = int(p.get("qt") or p.get("Qt") or p.get("pma") or p.get("Quotazione") or 1)
                        fm = float(p.get("fm") or p.get("Fm") or p.get("Fantamedia") or 6.0)
                        tit = int(p.get("tit") or p.get("Tit") or p.get("Titolarita") or 75)

                        players_db.append({
                            "id": idx + 1,
                            "nome": str(nome).strip().title(),
                            "squadra": squadra,
                            "ruolo": ruolo,
                            "fantamedia": fm,
                            "titolarita": tit,
                            "pma": pma,
                            "stemma": TEAM_LOGOS.get(squadra, "")
                        })
                    
                    print(f"📡 Fonte agganciata con successo! Trovati {len(players_db)} calciatori.")
                    break
        except Exception as e:
            continue

    if len(players_db) > 100:
        with open("players.json", "w", encoding="utf-8") as f:
            json.dump(players_db, f, ensure_ascii=False, indent=2)
        print(f"🔥 'players.json' aggiornato! Ora la tua lista ha {len(players_db)} giocatori.")
    else:
        print("❌ Errore nel recupero del listone completo.")

if __name__ == "__main__":
    update_database()
