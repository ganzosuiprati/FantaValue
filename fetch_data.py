import json
import requests
from bs4 import BeautifulSoup

def get_live_data():
    # URL di riferimento per le probabili formazioni
    url = "https://www.fantacalcio.it/probabili-formazioni-serie-a"
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    partite = []
    
    # Esempio di estrazione dei match
    match_cards = soup.find_all('div', class_='card-match') # Selettore di esempio
    
    for card in match_cards:
        # Estrazione nomi squadre e giocatori titolari/ballottaggi
        # (Adatta i selettori CSS in base alla struttura del sito sorgente)
        pass

    # Struttura dati JSON finale
    data = {
        "last_update": "2026-09-03",
        "partite": partite
    }

    with open('fantacola_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    get_live_data()
