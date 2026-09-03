import requests
from bs4 import BeautifulSoup
import json
import re
import sys

def clean_name(text):
    # Rimuove percentuali e caratteri inutili
    text = re.sub(r'\d+%', '', text)
    text = re.sub(r'^\d+\s*', '', text)
    return text.strip()

def fetch_probabili_formazioni():
    url = "https://www.fantacalcio.it/probabili-formazioni-serie-a"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }

    partite_data = []

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.content, "html.parser")

        # Seleziona le card delle partite
        cards = soup.select(".card-match, .match-card, .match-item")
        
        for card in cards:
            teams = card.select(".team-name, .title, .name")
            if len(teams) < 2:
                continue
            
            casa_nome = teams[0].get_text(strip=True).upper()
            trasferta_nome = teams[1].get_text(strip=True).upper()

            # Estrazione dei due blocchi squadra distinti per evitare duplicati
            team_blocks = card.select(".team-lineup, .lineup-team, .team-box")
            
            players_casa = []
            players_trasferta = []

            if len(team_blocks) >= 2:
                for block, target_list in [(team_blocks[0], players_casa), (team_blocks[1], players_trasferta)]:
                    # Usiamo un set per tracciare i nomi ed evitare doppioni nello stesso blocco
                    seen_names = set()
                    items = block.select(".player, .lineup-player, .player-item")
                    
                    for item in items:
                        raw_text = item.get_text(" ", strip=True)
                        nome = clean_name(raw_text)
                        
                        if not nome or nome in seen_names or len(nome) < 3:
                            continue
                        
                        seen_names.add(nome)

                        # Estrazione percentuale vera
                        perc_match = re.search(r'(\d{1,3})%', raw_text)
                        perc = int(perc_match.group(1)) if perc_match else 50

                        # Individuazione del ruolo se presente nelle classi o nel testo
                        role = "M" # Default
                        item_class = " ".join(item.get("class", [])).lower()
                        if "por" in item_class or "gk" in item_class: role = "P"
                        elif "dif" in item_class or "def" in item_class: role = "D"
                        elif "cen" in item_class or "mid" in item_class: role = "C"
                        elif "att" in item_class or "fwd" in item_class: role = "A"

                        target_list.append({
                            "nome": nome,
                            "percentuale": perc,
                            "ruolo": role
                        })

            if players_casa or players_trasferta:
                partite_data.append({
                    "match": f"{casa_nome} vs {trasferta_nome}",
                    "squadra_casa": casa_nome,
                    "squadra_trasferta": trasferta_nome,
                    "formazione_casa": players_casa,
                    "formazione_trasferta": players_trasferta
                })

    except Exception as e:
        print(f"Errore durante l'elaborazione: {e}")
        sys.exit(1)

    output = {
        "updated_at": "Aggiornato in tempo reale",
        "partite": partite_data
    }

    with open("fantacola_data.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print("Dati aggiornati correttamente senza duplicati.")

if __name__ == "__main__":
    fetch_probabili_formazioni()
