import json
import requests
import pandas as pd
import io

# Endpoint ufficiale del listone completo in Excel
EXCEL_URL = "https://www.fantacalcio.it/servizi/excel/quotazioni/2026"

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
    if r in ["P", "POR"]: return "P"
    if r in ["D", "DIF"]: return "D"
    if r in ["C", "CEN"]: return "C"
    return "A"

def update_data():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    print("🔄 Download del listone ufficiale da Fantacalcio.it...")
    
    try:
        res = requests.get(EXCEL_URL, headers=headers, timeout=15)
        if res.status_code == 200:
            # Legge il file ignorando le prime 1 righe di intestazione grafico
            df = pd.read_excel(io.BytesIO(res.content), skiprows=1)
            df.columns = [str(c).strip().lower() for c in df.columns]
            
            players_db = []
            for idx, row in df.iterrows():
                nome = row.get("nome") or row.get("calciatore")
                if pd.isna(nome): continue
                
                squadra = str(row.get("squadra", "SER"))[:3].upper()
                ruolo = clean_role(row.get("r") or row.get("ruolo", "A"))
                pma = int(row.get("qt.a") or row.get("qt.i") or row.get("quotazione") or 1)
                
                players_db.append({
                    "id": idx + 1,
                    "nome": str(nome).strip().title(),
                    "squadra": squadra,
                    "ruolo": ruolo,
                    "fantamedia": float(row.get("fm", 6.0)) if not pd.isna(row.get("fm")) else 6.0,
                    "titolarita": int(row.get("tit", 75)) if not pd.isna(row.get("tit")) else 75,
                    "pma": pma,
                    "stemma": TEAM_LOGOS.get(squadra, "")
                })

            with open("players.json", "w", encoding="utf-8") as f:
                json.dump(players_db, f, ensure_ascii=False, indent=2)
                
            print(f"🔥 SPETTACOLO! Salvati {len(players_db)} calciatori reali in 'players.json'!")
        else:
            print(f"❌ Errore HTTP {res.status_code}")
    except Exception as e:
        print(f"❌ Errore durante l'elaborazione: {e}")

if __name__ == "__main__":
    update_data()
