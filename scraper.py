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
    # Cerca la riga corretta delle intestazioni (riga 1 o riga 2)
    for skip in [1, 0, 2, 3]:
        try:
            temp_df = pd.read_excel(EXCEL_FILE, header=skip)
            cols = [str(c).strip() for c in temp_df.columns]
            
            # Controlla se le colonne fondamentali (Nome e Squadra) esistono
            if any('NOME' in c.upper() for c in cols) and any('SQUADRA' in c.upper() for c in cols):
                df = temp_df
                print(f"Intestazione valida trovata alla riga {skip + 1}!")
                break
        except Exception:
            continue

    if df is None:
        df = pd.read_excel(EXCEL_FILE, header=1)

    # Pulizia nomi colonne
    df.columns = [str(c).strip() for c in df.columns]

    print(f"Colonne rilevate nel file Excel: {list(df.columns)}")

    # Identificazione precisa colonne dallo screenshot
    col_nome = next((c for c in df.columns if c.upper() == 'NOME'), 'Nome')
    col_squadra = next((c for c in df.columns if c.upper() == 'SQUADRA'), 'Squadra')
    col_ruolo = next((c for c in df.columns if c.upper() in ['R', 'RM', 'RUOLO']), 'R')
    
    # Valore di Mercato (FVM) e Quotazione (Qt.A)
    col_fvm = next((c for c in df.columns if c.upper() in ['FVM', 'FVM M']), None)
    col_qta = next((c for c in df.columns if c.upper() in ['QT.A', 'QT.I', 'QTA', 'QUOTAZIONE']), None)
    
    # Eventuale Fantamedia o Titolarità se presenti in file estesi
    col_fm = next((c for c in df.columns if any(k in c.upper() for k in ['FM', 'FANTAMEDIA', 'MEDIA'])), None)
    col_tit = next((c for c in df.columns if any(k in c.upper() for k in ['TIT', 'TITOLARITA', '%'])), None)

    players = []

    for idx, row in df.iterrows():
        nome = str(row[col_nome]).strip() if pd.notnull(row[col_nome]) else ''
        if not nome or nome.lower() == 'nan' or nome.upper() == 'NOME':
            continue
        
        squadra = str(row[col_squadra]).strip()[:3].upper() if pd.notnull(row[col_squadra]) else "SER"
        ruolo = clean_role(row[col_ruolo]) if col_ruolo in row else 'C'
        
        # Lettura Quotazione e FVM
        qta = int(row[col_qta]) if col_qta and pd.notnull(row[col_qta]) and str(row[col_qta]).isdigit() else 1
        fvm = int(row[col_fvm]) if col_fvm and pd.notnull(row[col_fvm]) and str(row[col_fvm]).isdigit() else qta

        # Se FVM c'è, lo usiamo come base per il calcolo del prezzo di partenza (PMA)
        pma_base = fvm if fvm > 0 else qta

        # Fantamedia
        if col_fm and pd.notnull(row[col_fm]):
            try:
                fm = round(float(str(row[col_fm]).replace(',', '.')), 2)
            except:
                fm = 6.0
        else:
            # Se la FM non c'è nel listone quotazioni, stimiamo un valore coerente dal FVM
            if pma_base > 50: fm = 8.5
            elif pma_base > 30: fm = 7.5
            elif pma_base > 15: fm = 6.8
            else: fm = 6.0

        # Titolarità
        if col_tit and pd.notnull(row[col_tit]):
            try:
                tit = int(float(str(row[col_tit]).replace('%', '').replace(',', '.')))
            except:
                tit = 75
        else:
            # Stima Titolarità basata sul valore di quotazione
            tit = 90 if pma_base > 20 else (75 if pma_base > 5 else 50)

        players.append({
            "id": idx + 1,
            "nome": nome,
            "squadra": squadra,
            "ruolo": ruolo,
            "fantamedia": fm,
            "titolarita": tit,
            "pma": max(1, pma_base)
        })

    with open("players.json", "w", encoding="utf-8") as f:
        json.dump(players, f, ensure_ascii=False, indent=2)

    print(f"SUCCESS: Convertiti {len(players)} calciatori con FVM e Quotazioni reali!")

if __name__ == "__main__":
    main()
