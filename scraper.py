import requests
import pandas as pd
import json
import os
import sys

# URL del file ufficiale delle quotazioni Fantacalcio
EXCEL_URL = "https://www.fantacalcio.it/servizi/Excel.ashx?type=1"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def clean_role(role_raw):
    r = str(role_raw).upper().strip()
    if 'P' in r: return 'P'
    if 'D' in r: return 'D'
    if 'C' in r: return 'C'
    if 'A' in r: return 'A'
    return 'C'

def main():
    print("Download file quotazioni in corso...")
    excel_path = "quotazioni.xlsx"
    
    try:
        res = requests.get(EXCEL_URL, headers=headers, timeout=20)
        if res.status_code == 200:
            with open(excel_path, "wb") as f:
                f.write(res.content)
            print("File Excel scaricato con successo.")
        else:
            print(f"HTTP Error {res.status_code}")
    except Exception as e:
        print(f"Errore download: {e}")

    players = []

    if os.path.exists(excel_path):
        try:
            # Il file Excel di Fantacalcio ha le intestazioni alla riga 1
            df = pd.read_excel(excel_path, header=1)
            df.columns = [str(c).strip().upper() for c in df.columns]
            
            # Identificazione automatica delle colonne
            col_nome = next((c for c in df.columns if 'NOME' in c), None)
            col_squadra = next((c for c in df.columns if 'SQUADRA' in c or 'SQUAD' in c), None)
            col_ruolo = next((c for c in df.columns if 'R' in c or 'RUOLO' in c), None)
            col_pma = next((c for c in df.columns if 'FVM' in c or 'QT' in c or 'PMA' in c), None)

            if col_nome and col_ruolo:
                for idx, row in df.iterrows():
                    nome = str(row[col_nome]).strip()
                    if not nome or nome.lower() == 'nan':
                        continue
                    
                    squadra = str(row[col_squadra]).strip()[:3].upper() if col_squadra else "SER"
                    ruolo = clean_role(row[col_ruolo])
                    
                    try:
                        pma = int(row[col_pma]) if col_pma and pd.notnull(row[col_pma]) else 10
                    except:
                        pma = 10

                    players.append({
                        "id": idx + 1,
                        "nome": nome,
                        "squadra": squadra,
                        "ruolo": ruolo,
                        "fantamedia": 6.5,
                        "titolarita": 85,
                        "pma": max(1, pma)
                    })
        except Exception as e:
            print(f"Errore durante l'elaborazione dell'Excel: {e}")

    # Se il download è fallito o i dati sono insufficienti, preserviamo il json esistente
    if len(players) < 50:
        print("ATTENZIONE: Mantenimento players.json precedente per evitare perdite.")
        if os.path.exists("players.json"):
            sys.exit(0)

    # Scrittura del file JSON finale
    with open("players.json", "w", encoding="utf-8") as f:
        json.dump(players, f, ensure_ascii=False, indent=2)

    print(f"COMPLETATO! Salvati {len(players)} calciatori in players.json.")

if __name__ == "__main__":
    main()
