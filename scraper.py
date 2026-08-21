import json
import requests

# Feed JSON aggiornato con la Serie A completa
DATA_URL = "https://raw.githubusercontent.com/fede-co/fantacalcio-api/main/quotazioni.json"

# Mapping loghi ufficiali ad alta risoluzione (testati per Dark Mode)
TEAM_LOGOS = {
    "ATA": "https://upload.wikimedia.org/wikipedia/it/7/77/Atalanta_BC_logo.svg",
    "BOL": "https://upload.wikimedia.org/wikipedia/it/d/d8/Bologna_FC_1909_logo.svg",
    "CAG": "https://upload.wikimedia.org/wikipedia/it/3/3d/Cagliari_Calcio_2015.svg",
    "COM": "https://upload.wikimedia.org/wikipedia/it/2/29/Como_1907_logo.svg",
    "EMP": "https://upload.wikimedia.org/wikipedia/it/a/a3/Empoli_FC_logo_%282021%29.svg",
    "FIO": "https://upload.wikimedia.org/wikipedia/it/c/c2/ACF_Fiorentina_2022.svg",
    "GEN": "https://upload.wikimedia.org/wikipedia/it/3/37/Genoa_cfc.svg",
    "INT": "https://upload.wikimedia.org/wikipedia/commons/0/05/FC_Internazionale_Milano_2021.svg",
    "JUV": "https://upload.wikimedia.org/wikipedia/commons/b/bc/Juven_logo.png", # Stemma Bianco
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
    print("🔄 Download listone intero Serie A...")
    headers = {'User-Agent': 'Mozilla/5.0'}
    players_db = []

    try:
        res = requests.get(DATA_URL, headers=headers, timeout=12)
        if res.status_code == 200:
            data = res.json()
            for idx, p in enumerate(data):
                nome = p.get("nome") or p.get("Nome") or p.get("name")
                if not nome: continue
                
                squadra = str(p.get("squadra") or p.get("Squadra") or "SER")[:3].upper()
                ruolo = clean_role(p.get("ruolo") or p.get("R") or "A")
                pma = int(p.get("qt") or p.get("Qt") or p.get("pma") or 1)
                fm = float(p.get("fm") or p.get("Fm") or 6.0)
                tit = int(p.get("tit") or p.get("Tit") or 75)

                stemma = TEAM_LOGOS.get(squadra, "")

                players_db.append({
                    "id": p.get("id", idx + 1),
                    "nome": str(nome).title(),
                    "squadra": squadra,
                    "ruolo": ruolo,
                    "fantamedia": fm,
                    "titolarita": tit,
                    "pma": pma,
                    "stemma": stemma
                })
    except Exception as e:
        print(f"❌ Errore durante l'estrazione: {e}")

    if len(players_db) > 100:
        with open("players.json", "w", encoding="utf-8") as f:
            json.dump(players_db, f, ensure_ascii=False, indent=2)
        print(f"✅ 'players.json' salvato correttamente con {len(players_db)} calciatori!")
    else:
        print("⚠️ Errore download. Dati non aggiornati.")

if __name__ == "__main__":
    update_database()
