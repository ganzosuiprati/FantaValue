import pandas as pd
import json
import os
import sys

EXCEL_FILE = "listone.xlsx"

def clean_role(role_raw):
    r = str(role_raw).upper().strip()
    if 'P' in r: return 'P'
    if 'D' in r: return 'D'
    if 'C' in r: return 'C'
    if 'A' in r: return 'A'
    return 'C'

def main():
    if not os.path.exists(EXCEL_FILE):
        print(f"Errore: Il file {EXCEL_FILE} non esiste.")
        sys.exit(1)

    print(f"Lettura di {EXCEL_FILE}...")
    
    df = None
    # Cerca l'intestazione corretta nelle prime 5 righe dell'Excel
    for skip in range(5):
        try:
            temp_df = pd.read_excel(EXCEL_FILE, header=skip)
            cols = [str(c).strip().upper() for c in temp_df.columns]
            
            # Controlla se la riga corrente contiene colonne chiave
            has_nome = any('NOME' in c or 'GIOCATORE' in c or 'CALCIATORE' in c for c in cols)
            has_ruolo = any('RUOLO' in c or 'R' in c or 'RM' in c for c in cols)
            
            if has_nome and has_ruolo:
                df = temp_df
                df.columns = cols
                print(f"Intestazione trovata alla riga {skip + 1}!")
                break
        except Exception as e:
            continue

    if df is None:
        print("Impossibile identificare le intestazioni nell'Excel. Uso la prima riga di default.")
        df = pd.read_excel(EXCEL_FILE, header=0)
        df.columns = [str(c).strip().upper() for c in df.columns]

    print(f"Colonne rilevate: {list(df.columns)}")

    # Mappatura flessibile di tutte le varianti di nomi colonna
    col_nome = next((c for c in df.columns if any(k in c for k in ['NOME', 'GIOCATORE', 'CALCIATORE'])), None)
    col_squadra = next((c for c in df.columns if any(k in c for k in ['SQUADRA', 'SQ', 'CLUB', 'TEAM'])), None)
    col_ruolo = next((c for c in df.columns if any(k in c for k in ['RUOLO', 'RM', 'R'])), None)
    col_pma = next((c for c in df.columns if any(k in c for k in ['FVM', 'QT', 'PMA', 'PREZZO', 'QUOT', 'VALORE'])), None)
    col_fm = next((c for c in df.columns if any(k in c for k in ['FM', 'MEDIA', 'FANTAMEDIA'])), None)
    col_tit = next((c for c in df.columns if any(k in c for k in ['TIT', 'TITOLAR', '%'])), None)

    players = []

    if col_nome and col_ruolo:
        for idx, row in df.iterrows():
            nome = str(row[col_nome]).strip()
            if not nome or nome.lower() == 'nan' or nome.upper() == 'NOME':
                continue
            
            squadra = str(row[col_squadra]).strip()[:3].upper() if col_squadra and pd.notnull(row[col_squadra]) else "SER"
            ruolo = clean_role(row[col_ruolo])
            
            # Conversione Prezzo/Quotazione
            try:
                val_pma = str(row[col_pma]).replace(',', '.').strip() if col_pma and pd.notnull(row[col_pma]) else '10'
                pma = int(float(val_pma))
            except:
                pma = 10

            # Conversione Fantamedia
            try:
                val_fm = str(row[col_fm]).replace(',', '.').strip() if col_fm and pd.notnull(row[col_fm]) else '6.5'
                fm = float(val_fm)
            except:
                fm = 6.5

            # Conversione Titolarità
            try:
                val_tit = str(row[col_tit]).replace('%', '').strip() if col_tit and pd.notnull(row[col_tit]) else '85'
                tit = int(float(val_tit))
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

        if len(players) > 0:
            with open("players.json", "w", encoding="utf-8") as f:
                json.dump(players, f, ensure_ascii=False, indent=2)
            print(f"SUCCESS: Convertiti {len(players)} calciatori da Excel a players.json!")
        else:
            print("Nessun giocatore valido trovato nell'Excel.")
    else:
        print("ERRORE: Colonne NOME o RUOLO non trovate nell'Excel.")
        sys.exit(1)

if __name__ == "__main__":
    main()
