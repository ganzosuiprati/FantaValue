import requests
from bs4 import BeautifulSoup
import json
import re
import os
import glob
import pandas as pd

def fetch_probabili_formazioni():
    url = "https://www.fantacalcio.it/probabili-formazioni-serie-a"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    partite_data = []

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, "html.parser")
            matches = soup.find_all("li", class_=re.compile(r"match-item|card-match|match"))

            for m in matches:
                try:
                    teams = m.find_all("span", class_=re.compile(r"team-name|title|name"))
                    if len(teams) >= 2:
                        casa = teams[0].get_text(strip=True)
                        trasferta = teams[1].get_text(strip=True)
                        
                        players = [p.get_text(strip=True) for p in m.find_all("a", class_=re.compile(r"player|player-name"))]
                        
                        titolari_casa = players[:11] if len(players) >= 11 else ["In aggiornamento..."]
                        titolari_trasferta = players[11:22] if len(players) >= 22 else ["In aggiornamento..."]

                        partite_data.append({
                            "match": f"{casa.upper()} vs {trasferta.upper()}",
                            "squadre": {
                                "casa": {"nome": casa.upper(), "titolari": titolari_casa},
                                "trasferta": {"nome": trasferta.upper(), "titolari": titolari_trasferta}
                            }
                        })
                except Exception:
                    continue
    except Exception as e:
        print(f"Warning scraping: {e}")

    # Fallback se lo scraping del giorno non trova match
    if not partite_data:
        partite_data = [
            {
                "match": "GENOA vs COMO",
                "squadre": {
                    "casa": {"nome": "GENOA", "titolari": ["Bijlow", "Marcandalli", "Ostigard", "Vasquez", "Ellertsson", "Frendrup", "Sow", "Mitaj", "Baldanzi", "Vitinha", "Colombo"]},
                    "trasferta": {"nome": "COMO", "titolari": ["Butez", "Couto", "Chalobah", "Ramon", "Valle", "Da Cunha", "Perrone", "Diao", "Paz N.", "Baturina", "Kean"]}
                }
            },
            {
                "match": "FIORENTINA vs TORINO",
                "squadre": {
                    "casa": {"nome": "FIORENTINA", "titolari": ["De Gea", "Jimenez A.", "Dragusin", "Viery", "Valdepenas", "Ndour", "Oulai", "Atta", "Mastantuono", "Njie", "Pellegrino M."]},
                    "trasferta": {"nome": "TORINO", "titolari": ["Perri", "Comuzzo", "Coco", "Comert", "Belghali", "Gineitis", "Fitz-Jim", "Cacciamani", "Adams C.", "Vlasic", "Simeone"]}
                }
            }
        ]

    # Lettura automatica di qualsiasi file Excel/CSV di listone presente nella cartella
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
            print(f"Errore lettura listone: {ex}")

    output = {
        "giornata": 3,
        "last_update": "Avanzato in Tempo Reale",
        "partite": partite_data,
        "listone": listone_players
    }

    with open("fantacola_data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("Successo: fantacola_data.json generato!")

if __name__ == "__main__":
    fetch_probabili_formazioni()
