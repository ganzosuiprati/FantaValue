import pandas as pd
import json
import os
import sys

EXCEL_FILE = "Quotazioni_Fantacalcio_Stagione_2026_27.xlsx"

RIGORISTI_PRIMI = [
    "Calhanoglu", "Vlahovic", "Pulisic", "De Bruyne", "Scamacca", 
    "Dybala", "Zaccagni", "Gudmundsson", "Orsolini", "Vlasic", 
    "Da Cunha", "Messias", "Nzola", "Pessina", "Bernabé", 
    "Berardi", "Davis", "Geubbels", "Busio", "Calò"
]

def clean_role(role_raw):
    r = str(role_raw).upper().strip()
    if 'P' in r: return 'P'
    if 'D' in r: return 'D'
    if 'C' in r: return 'C'
    if 'A' in r: return 'A'
    return 'C'

def is_primo_rigorista(nome):
    nome_clean = str(nome).lower().strip()
    for rig in RIGORISTI_PRIMI:
        rig_clean = rig.lower().strip()
        if rig_clean in nome_clean or nome_clean in rig_clean:
            return True
    return False

def clean_int(val, default=1):
    try:
        if pd.isna(val): return default
        num = int(float(str(val).replace(',', '.')))
        return num if num > 0 else default
    except:
        return default

def clean_float(val, default=6.0):
    try:
        if pd.isna(val): return default
        return round(float(str(val).replace(',', '.')), 2)
    except:
        return default

def main():
    target_file = EXCEL_FILE if os.path.exists(EXCEL_FILE) else "Quotazioni_Fantacalcio_Stagione_2026_27_2.xlsx"
    if not os.path.exists(target_file):
        print("Errore: File Excel non trovato.")
        sys.exit(1)

    df = pd.read_excel(target_file, sheet_name=0, header=1)
    df.columns = [str(c).strip() for c in df.columns]

    col_nome = next((c for c in df.columns if c.upper() == 'NOME'), 'Nome')
    col_squadra = next((c for c in df.columns if c.upper() == 'SQUADRA'), 'Squadra')
    col_ruolo = next((c for c in df.columns if c.upper() in ['R', 'RM', 'RUOLO']), 'R')
    col_fvm = next((c for c in df.columns if c.upper() in ['FVM', 'FVM M']), None)
    col_qta = next((c for c in df.columns if c.upper() in ['QT.A', 'QT.I', 'QTA', 'QUOTAZIONE']), None)
    col_fm = next((c for c in df.columns if any(k in c.upper() for k in ['FM', 'FANTAMEDIA', 'MEDIA'])), None)
    col_tit = next((c for c in df.columns if any(k in c.upper() for k in ['TIT', 'TITOLARITA', '%'])), None)

    players = []

    for idx, row in df.iterrows():
        nome = str(row[col_nome]).strip() if pd.notnull(row[col_nome]) else ''
        if not nome or nome.lower() == 'nan' or nome.upper() == 'NOME':
            continue
        
        squadra = str(row[col_squadra]).strip()[:12].upper() if pd.notnull(row[col_squadra]) else "SER"
        ruolo = clean_role(row[col_ruolo]) if col_ruolo in row else 'C'
        
        qta = clean_int(row[col_qta] if col_qta and col_qta in row else 1, default=1)
        fvm = clean_int(row[col_fvm] if col_fvm and col_fvm in row else qta, default=qta)

        pma_base = fvm if fvm > 0 else qta

        fm = clean_float(row[col_fm] if col_fm and col_fm in row else 6.0, default=6.0)
        tit = clean_int(row[col_tit] if col_tit and col_tit in row else 75, default=75)

        tags = []
        if is_primo_rigorista(nome):
            tags.append("RIGORISTA")

        players.append({
            "id": idx + 1,
            "nome": nome,
            "squadra": squadra,
            "ruolo": ruolo,
            "fantamedia": fm,
            "titolarita": tit,
            "pma_base": int(pma_base),
            "pma": int(pma_base),
            "tags": tags
        })

    with open("players.json", "w", encoding="utf-8") as f:
        json.dump(players, f, ensure_ascii=False, indent=2)

    print(f"Salvati {len(players)} giocatori in players.json!")

if __name__ == "__main__":
    main()
