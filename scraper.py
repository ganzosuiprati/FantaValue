import pandas as pd
import json
import os
import sys

EXCEL_FILE = "Quotazioni_Fantacalcio_Stagione_2026_27.xlsx"

# 1° Rigorista ufficiale per squadra
RIGORISTI_PRIMI = [
    "Calhanoglu",        # Inter
    "Vlahovic",          # Juventus
    "Pulisic",           # Milan
    "De Bruyne",         # Napoli
    "Scamacca",          # Atalanta
    "Dybala",            # Roma
    "Zaccagni",          # Lazio
    "Gudmundsson",       # Fiorentina
    "Orsolini",          # Bologna
    "Vlasic",            # Torino
    "Da Cunha",          # Como
    "Messias",           # Genoa
    "Nzola",             # Cagliari
    "Pessina",           # Monza
    "Bernabé",           # Parma
    "Berardi",           # Sassuolo
    "Davis",             # Udinese
    "Geubbels",          # Lecce
    "Busio",             # Venezia
    "Calò"               # Frosinone
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

def main():
    target_file = EXCEL_FILE if os.path.exists(EXCEL_FILE) else "Quotazioni_Fantacalcio_Stagione_2026_27_2.xlsx"
    if not os.path.exists(target_file):
        print(f"Errore: File Excel non trovato.")
        sys.exit(1)

    print(f"Elaborazione di: {target_file}")

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
        
        qta = int(row[col_qta]) if col_qta and pd.notnull(row[col_qta]) and str(row[col_qta]).isdigit() else 1
        fvm = int(row[col_fvm]) if col_fvm and pd.notnull(row[col_fvm]) and str(row[col_fvm]).isdigit() else qta

        pma_base = fvm if fvm > 0 else qta

        if col_fm and pd.notnull(row[col_fm]):
            try:
                fm = round(float(str(row[col_fm]).replace(',', '.')), 2)
            except:
                fm = 6.0
        else:
            fm = 6.0

        if col_tit and pd.notnull(row[col_tit]):
            try:
                tit = int(float(str(row[col_tit]).replace('%', '').replace(',', '.')))
            except:
                tit = 75
        else:
            tit = 75

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
            "pma_base": max(1, pma_base), # Base parametrata a 1000 CR / 8 partecipanti
            "tags": tags
        })

    with open("players.json", "w", encoding="utf-8") as f:
        json.dump(players, f, ensure_ascii=False, indent=2)

    print(f"SUCCESSO: Esportati {len(players)} calciatori in players.json!")

if __name__ == "__main__":
    main()
