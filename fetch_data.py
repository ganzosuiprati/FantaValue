import requests
from bs4 import BeautifulSoup
import json
import re
import glob
import pandas as pd
import sys

def fetch_probabili_formazioni():
    url = "https://www.fantacalcio.it/probabili-formazioni-serie-a"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    partite_data = []

    try:
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "html.parser")

        # Cerca i blocchi delle partite su Fantacalcio.it
        match_cards = soup.find_all("div", class_=re.compile(r"card-match|match-card|match-item"))
        if not match_cards:
            match_cards = soup.find_all("li", class_=re.compile(r"match-item|card-match"))

        for card in match_cards:
            try:
                # Estrazione Nomi Squadre
                teams = card.find_all(["span", "h3", "h4", "div", "a"], class_=re.compile(r"team-name|title|name|team"))
                if len(teams) < 2:
                    continue
                
                casa_nome = teams[0].get_text(strip=True).upper()
                trasferta_nome = teams[1].get_text(strip=True).upper()

                if not casa_nome or not trasferta_nome or casa_nome == trasferta_nome:
                    continue

                # Estrazione Giocatori e Percentuali
                players_casa = []
                players_trasferta = []

                # Sezioni Casa e Trasferta
                team_blocks = card.find_all("div", class_=re.compile(r"team-lineup|lineup-team|team-box|team"))
                
                if len(team_blocks) >= 2:
                    blocks_to_process = [(team_blocks[0], players_casa), (team_blocks[1], players_trasferta)]
                else:
                    # Alternativa: scansione globale dei player items
                    blocks_to_process = []

                if blocks_to_process:
                    for block, target_list in blocks_to_process:
                        p_items = block.find_all(["div", "li", "a"], class_=re.compile(r"player|lineup-player|player-item"))
                        for item in p_items:
                            text = item.get_text(" ", strip=True)
                            perc_match = re.search(r'(\d{1,3})%', text)
                            perc = int(perc_match.group(1)) if perc_match else 75
                            
                            # Pulizia nome
                            name_clean = re.sub(r'\d+%', '', text).strip()
                            name_clean = re.sub(r'^\d+\s*', '', name_clean) # rimuove numeri maglia se presenti
                            
                            if name_clean and len(name_clean) > 2 and not any(x in name_clean.lower() for x in ['panchina', 'squalificati', 'infortunati']):
                                target_list.append({"nome": name_clean, "percentuale": perc})
                else:
                    # Parsing generico se non divisibile per blocchi
                    all_p = card.find_all(["div", "li", "a"], class_=re.compile(r"player|lineup-player"))
                    for idx, item in enumerate(all_p):
                        text = item.get_text(" ", strip=True)
                        perc_match = re.search(r'(\d{1,3})%', text)
                        perc = int(perc_match.group(1)) if perc_match else 75
                        name_clean = re.sub(r'\d+%', '', text).strip()
                        
                        if name_clean and len(name_clean) > 2:
                            obj = {"nome": name_clean, "percentuale": perc}
                            if len(players_casa) < 11:
                                players_casa.append(obj)
                            else:
                                players_trasferta.append(obj)

                if casa_nome and trasferta_nome:
                    partite_data.append({
                        "match": f"{casa_nome} vs {trasferta_nome}",
                        "squadre": {
                            "casa": {"nome": casa_nome, "titolari": players_casa},
                            "trasferta": {"nome": trasferta_nome, "titolari": players_trasferta}
                        }
                    })

            except Exception as e:
                continue

    except Exception as err:
        print(f"Errore critico durante lo scraping da Fantacalcio.it: {err}")
        sys.exit(1)

    if not partite_data:
        print("ATTENZIONE: Nessuna partita estratta da Fantacalcio.it. Verificare la struttura della pagina.")
        sys.exit(1)

    # Caricamento del Listone Excel/CSV reale presente nella cartella GitHub
    listone_players = []
    data_files = glob.glob("*.xlsx") + glob.glob("*.csv")
    if data_files:
        try:
            file_path = data_files[0]
            if file_path.endswith('.xlsx'):
                df = pd.read_excel(file_path, sheet_name=0, header=1)
            else:
                df = pd.read_csv(file_path)
            
            df.columns = [str(c).strip().upper() for c in df.columns]
            col_nome = next((c for c in df.columns if 'NOME' in c), None)
            col_squadra = next((c for c in df.columns if 'SQUADRA' in c), None)
            col_ruolo = next((c for c in df.columns if c in ['R', 'RM', 'RUOLO']), None)

            if col_nome and col_ruolo:
                for _, row in df.iterrows():
                    n = str(row[col_nome]).strip()
                    if n and n.lower() != 'nan':
                        listone_players.append({
                            "nome": n,
                            "squadra": str(row[col_squadra]).strip() if col_squadra else "SER",
                            "ruolo": str(row[col_ruolo]).upper().strip()[0]
                        })
        except Exception as ex:
            print(f"Errore lettura listone locale: {ex}")

    output = {
        "giornata": "Giornata Serie A Live",
        "last_update": "Aggiornato in Tempo Reale da Fantacalcio.it",
        "partite": partite_data,
        "listone": listone_players
    }

    with open("fantacola_data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"SUCCESS: Scaricate {len(partite_data)} partite reali da Fantacalcio.it!")

if __name__ == "__main__":
    fetch_probabili_formazioni()
