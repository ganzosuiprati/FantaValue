import pandas as pd
import json
import os

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
        print(f"Errore: il file {EXCEL_FILE} non esiste nel repository!")
        return

    print(f"Elaborazione del file {EXCEL_FILE}...")

    try:
        # Se il tuo Excel ha le intestazioni nella riga 2 o 3, cambia header=0 con header=1 o header=2
        df = pd.read_excel(EXCEL_FILE, header=0)
        
        # Pulizia intestazioni colonne
        df.columns = [str(c).strip().upper() for c in df.columns]
        print(f"Colonne trovate: {list(df.columns)}")

        # Mappatura automatica delle colonne principali
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
                
                try:
                    pma = int(float(str(row[col_pma]).replace(',', '.'))) if col_pma and pd.notnull(row[col_pma]) else 10
                except:
                    pma = 10

                try:
                    fm = float(str(row[col_fm]).replace(',', '.')) if col_fm and pd.notnull(row[col_fm]) else 6.5
                except:
                    fm = 6.5

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

            with open("players.json", "w", encoding="utf-8") as f:
                json.dump(players, f, ensure_ascii=False, indent=2)
            
            print(f"COMPLETATO! Convertiti {len(players)} calciatori da Excel a players.json.")
        else:
            print("Errore: impossibile trovare le colonne NOME e RUOLO nel file Excel.")

    except Exception as e:
        print(f"Errore durante l'elaborazione dell'Excel: {e}")

if __name__ == "__main__":
    main()
