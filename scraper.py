import json
import requests

# Endpoint per il listone completo
DATA_URL = "https://www.fantacalcio.it/api/v1/excel/get-dataset/2024"  # Fallback JSON API completa
SECONDARY_URL = "https://raw.githubusercontent.com/fede-co/fantacalcio-api/main/quotazioni.json"

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
    print("🔄 Download del listone COMPLETO Serie A in corso...")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    players_db = []

    # Prova API Fantacalcio / Dataset
    try:
        res = requests.get("https://raw.githubusercontent.com/vittorioparis/fantacalcio-dataset/main/data/quotazioni.json", headers=headers, timeout=12)
        if res.status_code != 200:
            res = requests.get(SECONDARY_URL, headers=headers, timeout=12)
        
        data = res.json()
        
        # Se il dato è dentro una chiave specifica (es. "data" o "players")
        raw_list = data.get("data", data) if isinstance(data, dict) else data

        for idx, p in enumerate(raw_list):
            nome = p.get("nome") or p.get("Nome") or p.get("name") or p.get("Player")
            if not nome: continue
            
            squadra = str(p.get("squadra") or p.get("Squadra") or p.get("Team") or "SER")[:3].upper()
            ruolo = clean_role(p.get("ruolo") or p.get("R") or p.get("Role") or "A")
            
            # Prezzo/Quotazione di partenza
            pma = int(p.get("qt") or p.get("Qt") or p.get("pma") or p.get("Quotazione") or 1)
            fm = float(p.get("fm") or p.get("Fm") or p.get("Fantamedia") or 6.0)
            tit = int(p.get("tit") or p.get("Tit") or p.get("Titolarita") or 75)

            stemma = TEAM_LOGOS.get(squadra, "")

            players_db.append({
                "id": p.get("id", idx + 1),
                "nome": str(nome).strip().title(),
                "squadra": squadra,
                "ruolo": ruolo,
                "fantamedia": fm,
                "titolarita": tit,
                "pma": pma,
                "stemma": stemma
            })

    except Exception as e:
        print(f"❌ Errore durante l'estrazione: {e}")

    if len(players_db) > 0:
        with open("players.json", "w", encoding="utf-8") as f:
            json.dump(players_db, f, ensure_ascii=False, indent=2)
        print(f"✅ 'players.json' generato con successo! Trovati {len(players_db)} calciatori.")
    else:
        print("⚠️ Nessun giocatore estratto, controlla la fonte.")

if __name__ == "__main__":
    update_database()
