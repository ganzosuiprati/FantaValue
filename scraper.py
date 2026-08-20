import json
import re
import urllib.parse
import requests
from bs4 import BeautifulSoup


def get_wikipedia_photo(player_name):
    """Cerca su Wikipedia Italia la foto/thumbnail ufficiale del calciatore."""
    try:
        search_url = f"https://it.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(player_name)}&prop=pageimages&format=json&pithumbsize=150"
        response = requests.get(search_url, timeout=3)
        data = response.json()
        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if "thumbnail" in page_data:
                return page_data["thumbnail"]["source"]
    except Exception:
        pass
    return ""


def clean_role(role_raw):
    """Mappa e normalizza il ruolo in P, D, C, A."""
    role_str = str(role_raw).strip().upper()
    if role_str in ["POR", "P", "1"]:
        return "P"
    if role_str in ["DIF", "D", "2"]:
        return "D"
    if role_str in ["CEN", "C", "3"]:
        return "C"
    if role_str in ["ATT", "A", "4"]:
        return "A"
    return "A"


def scrape_and_generate_json():
    print("🔄 Avvio scraping e rigenerazione database...")

    # ESEMPIO: Sostituisci questo URL con la fonte reale da cui prelevi i dati
    # oppure con la logica di estrazione che avevi impostato.
    url = "https://www.fantacalcio.it/quotazioni-fantacalcio"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    players_database = []

    try:
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        # Selettore di esempio sui righelli della tabella
        rows = soup.find_all("tr", class_=re.compile("player"))

        for row in rows:
            try:
                # Estrazione e mappatura corretta dei campi
                nome_el = row.find(class_=re.compile("name|giocatore"))
                squadra_el = row.find(class_=re.compile("team|squadra"))
                ruolo_el = row.find(class_=re.compile("role|ruolo"))
                fm_el = row.find(class_=re.compile("fm|fantamedia"))
                tit_el = row.find(class_=re.compile("tit|titolarita"))
                pma_el = row.find(class_=re.compile("qt|quotazione|pma"))

                nome = nome_el.text.strip() if nome_el else "Sconosciuto"
                squadra = squadra_el.text.strip() if squadra_el else "Serie A"
                ruolo = (
                    clean_role(ruolo_el.text.strip()) if ruolo_el else "A"
                )

                fantamedia = (
                    float(fm_el.text.strip().replace(",", "."))
                    if fm_el
                    else 6.0
                )
                titolarita = (
                    int(re.sub(r"\D", "", tit_el.text.strip()))
                    if tit_el
                    else 80
                )
                pma = int(re.sub(r"\D", "", pma_el.text.strip())) if pma_el else 10

                # Recupera foto Wikipedia (opzionale o da cache)
                foto = get_wikipedia_photo(f"{nome} calciatore")

                player_obj = {
                    "nome": nome,
                    "squadra": squadra,
                    "ruolo": ruolo,
                    "fantamedia": fantamedia,
                    "titolarita": titolarita,
                    "pma": pma,
                    "foto": foto,
                }

                players_database.append(player_obj)
            except Exception as e:
                continue

    except Exception as err:
        print(f"❌ Errore durante il recupero web: {err}")

    # Se lo scraping fallisce o per dati di test diretti:
    if not players_database:
        print(
            "⚠️ Generazione struttura dati di fallback con valori realistici..."
        )
        players_database = [
            {
                "nome": "Lautaro Martinez",
                "squadra": "Inter",
                "ruolo": "A",
                "fantamedia": 8.8,
                "titolarita": 95,
                "pma": 280,
                "foto": get_wikipedia_photo("Lautaro Martínez"),
            },
            {
                "nome": "Federico Dimarco",
                "squadra": "Inter",
                "ruolo": "D",
                "fantamedia": 7.3,
                "titolarita": 90,
                "pma": 55,
                "foto": get_wikipedia_photo("Federico Dimarco"),
            },
            {
                "nome": "Ademola Lookman",
                "squadra": "Atalanta",
                "ruolo": "A",
                "fantamedia": 8.2,
                "titolarita": 85,
                "pma": 190,
                "foto": get_wikipedia_photo("Ademola Lookman"),
            },
            {
                "nome": "Niccolò Barella",
                "squadra": "Inter",
                "ruolo": "C",
                "fantamedia": 7.1,
                "titolarita": 92,
                "pma": 60,
                "foto": get_wikipedia_photo("Nicolò Barella"),
            },
            {
                "nome": "Yann Sommer",
                "squadra": "Inter",
                "ruolo": "P",
                "fantamedia": 6.8,
                "titolarita": 98,
                "pma": 45,
                "foto": get_wikipedia_photo("Yann Sommer"),
            },
        ]

    # Salvataggio del file JSON pulito
    with open("players.json", "w", encoding="utf-8") as f:
        json.dump(players_database, f, ensure_ascii=False, indent=2)

    print(
        f"✅ File 'players.json' generato con successo! ({len(players_database)} giocatori salvati)"
    )


if __name__ == "__main__":
    scrape_and_generate_json()
