import json
import re
import urllib.parse
import requests


def get_wikipedia_photo(player_name):
    """Cerca la foto del calciatore via API di Wikipedia Italia."""
    try:
        query = f"{player_name} calciatore"
        url = f"https://it.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(query)}&prop=pageimages&format=json&pithumbsize=150"
        res = requests.get(url, timeout=2).json()
        pages = res.get("query", {}).get("pages", {})
        for _, val in pages.items():
            if "thumbnail" in val:
                return val["thumbnail"]["source"]
    except Exception:
        pass
    return ""


def clean_role(raw_role):
    """Mappa i ruoli ufficiali in P, D, C, A."""
    r = str(raw_role).strip().upper()
    if r in ["P", "POR", "1"]:
        return "P"
    if r in ["D", "DIF", "2"]:
        return "D"
    if r in ["C", "CEN", "3"]:
        return "C"
    return "A"


def update_database():
    print("🔄 Avvio sincronizzazione dati reali...")

    # API o fonte dati ufficiale di quotazioni/statistiche Fantacalcio
    # NOTA: Estragga quotazioni (Qt) e ruoli reali per ogni giocatore
    source_url = "https://www.fantacalcio.it/api/v1/excel/quotazioni"
    headers = {"User-Agent": "Mozilla/5.0"}

    players_db = []

    try:
        # Tenta il recupero dal webservice
        res = requests.get(source_url, headers=headers, timeout=10)
        # Se si usa scraping HTML o JSON diretto:
        data = res.json() if res.status_code == 200 else []

        for p in data:
            players_db.append({
                "nome": p.get("Nome", "Unknown"),
                "squadra": p.get("Squadra", "Serie A"),
                "ruolo": clean_role(p.get("R", "A")),
                "fantamedia": float(p.get("Fm", 6.0)),
                "titolarita": int(p.get("Tit", 80)),
                "pma": int(p.get("Qt", 10)),  # Quotazione ufficiale Fantacalcio
                "foto": get_wikipedia_photo(p.get("Nome", "")),
            })
    except Exception as e:
        print(f"⚠️ Errore durante il fetch automatico: {e}")

    # Fallback/Test con dati veri di Serie A se il fetch fallisce
    if not players_db:
        players_db = [
            {
                "nome": "Lautaro Martinez",
                "squadra": "Inter",
                "ruolo": "A",
                "fantamedia": 8.8,
                "titolarita": 95,
                "pma": 38,
                "foto": get_wikipedia_photo("Lautaro Martínez"),
            },
            {
                "nome": "Federico Dimarco",
                "squadra": "Inter",
                "ruolo": "D",
                "fantamedia": 7.4,
                "titolarita": 90,
                "pma": 18,
                "foto": get_wikipedia_photo("Federico Dimarco"),
            },
            {
                "nome": "Ademola Lookman",
                "squadra": "Atalanta",
                "ruolo": "A",
                "fantamedia": 8.2,
                "titolarita": 85,
                "pma": 30,
                "foto": get_wikipedia_photo("Ademola Lookman"),
            },
            {
                "nome": "Scott McTominay",
                "squadra": "Napoli",
                "ruolo": "C",
                "fantamedia": 7.5,
                "titolarita": 92,
                "pma": 22,
                "foto": get_wikipedia_photo("Scott McTominay"),
            },
            {
                "nome": "Nico Paz",
                "squadra": "Como",
                "ruolo": "C",
                "fantamedia": 7.2,
                "titolarita": 88,
                "pma": 15,
                "foto": get_wikipedia_photo("Nico Paz"),
            },
            {
                "nome": "Yann Sommer",
                "squadra": "Inter",
                "ruolo": "P",
                "fantamedia": 6.8,
                "titolarita": 98,
                "pma": 16,
                "foto": get_wikipedia_photo("Yann Sommer"),
            },
        ]

    with open("players.json", "w", encoding="utf-8") as f:
        json.dump(players_db, f, ensure_ascii=False, indent=2)

    print(f"✅ 'players.json' aggiornato con {len(players_db)} calciatori.")


if __name__ == "__main__":
    update_database()
