import pandas as pd
import json
import os
import sys

# URL per l'esportazione diretta in CSV del foglio Google
GOOGLE_SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1ZJgLTAdGyW3WtJPT9S6eN1sGUq4mtOJn8g-zjIGF9sE/export?format=csv&gid=1912644989"

def clean_role(role_raw):
    r = str(role_raw).upper().strip()
    if 'P' in r: return 'P'
    if 'D' in r: return 'D'
    if 'C' in r: return 'C'
    if 'A' in r: return 'A'
    return 'C'

def main():
    print("Download dati in tempo reale dal Google Sheet...")
    
    try:
        # Legge il CSV direttamente dall'URL di Google Sheets
        df = pd.read_csv(GOOGLE_SHEET_CSV_URL)
        print(f"Foglio scaricato con successo. Righe trovate: {len(df)}")
        
        # Pulizia intestazioni colonne (rimuove spazi e mette in maiuscolo)
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Mappatura dinamica delle colonne
        col_nome = next((c for c in df.columns if 'NOME' in c or 'CALCIATORE' in c or 'GIOCATORE' in c), None)
        col_squadra = next((c for c in df.columns if 'SQUADRA' in c or 'SQ' in c), None)
        col_ruolo = next((c for c in df.columns if 'R' in c or 'RUOLO' in c), None)
        col_pma = next((c for c in df.columns if 'FVM' in c or 'QT' in c or 'PMA' in c or 'QUOT' in c or 'PREZZO' in c), None)
        col_fm = next((c for c in df.columns if 'FM' in c or 'MEDIA' in c), None)
        col_tit = next((c for c in df.columns if 'TIT' in c or 'TITOLAR' in c), None)

        players = []

        if col_nome and col_ruolo:
            for idx, row in df.iterrows():
                nome = str(row[col_nome]).strip()
                if not nome or nome.lower() == 'nan':
                    continue
                
                squadra = str(row[col_squadra]).strip()[:3].upper() if col_squadra and pd.notnull(row[col_squadra]) else "SER"
                ruolo = clean_role(row[col_ruolo])
                
                # Conversione Prezzo/PMA
                try:
                    pma = int(float(str(row[col_pma]).replace(',', '.'))) if col_pma and pd.notnull(row[col_pma]) else 10
                except:
                    pma = 10

                # Conversione Fantamedia (se presente)
                try:
                    fm = float(str(row[col_fm]).replace(',', '.')) if col_fm and pd.notnull(row[col_fm]) else 6.5
                except:
                    fm = 6.5

                # Conversione Titolarità (se presente)
                try:
                    tit = int(float(str(row[col_tit]).replace('%', ''))) if col_tit and pd.notnull(row[col_tit]) else 85
                except:
                    tit = 85

                players.append({
                    "id": idx + 1,
                    "nome": nome,
                    "squadra": squadra,
                    "ruolo": ruolo,
                    "fantamedia": round(fm, 2),
                    "titolarita": tit,
                    "pma": max(1, pma)
                })

            # Salvataggio nel file players.json
            if len(players) > 0:
                with open("players.json", "w", encoding="utf-8") as f:
                    json.dump(players, f, ensure_ascii=False, indent=2)
                print(f"COMPLETATO! Salvati {len(players)} calciatori in players.json.")
            else:
                print("Nessun giocatore estratto correttamente dal foglio.")

        else:
            print(f"Colonne non riconosciute. Colonne presenti: {list(df.columns)}")

    except Exception as e:
        print(f"Errore durante il download da Google Sheets: {e}")
        if os.path.exists("players.json"):
            print("Mantenuto players.json esistente.")
            sys.exit(0)

if __name__ == "__main__":
    main()
