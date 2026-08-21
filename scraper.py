import json
import urllib.parse
import requests

# URL raw ad accesso libero con la lista aggiornata di tutte le rose Serie A
DATA_URL = "https://raw.githubusercontent.com/fede-co/fantacalcio-api/main/quotazioni.json"

# Mappa degli stemmi ufficiali della Serie A (utilizzati come fallback guaranteed)
TEAM_LOGOS = {
    "ATA": "https://a.espncdn.com/i/teamlogos/soccer/500/105.png",
    "BOL": "https://a.espncdn.com/i/teamlogos/soccer/500/107.png",
    "CAG": "https://a.espncdn.com/i/teamlogos/soccer/500/108.png",
    "COM": "https://a.espncdn.com/i/teamlogos/soccer/500/2932.png",
    "EMP": "https://a.espncdn.com/i/teamlogos/soccer/500/2622.png",
    "FIO": "https://a.espncdn.com/i/teamlogos/soccer/500/109.png",
    "GEN": "https://a.espncdn.com/i/teamlogos/soccer/500/3263.png",
    "INT": "https://a.espncdn.com/i/teamlogos/soccer/500/110.png",
    "JUV": "https://a.espncdn.com/i/teamlogos/soccer/500/111.png",
    "LAZ": "https://a.espncdn.com/i/teamlogos/soccer/500/112.png",
    "LEC": "https://a.espncdn.com/i/teamlogos/soccer/500/3440.png",
    "MIL": "https://a.espncdn.com/i/teamlogos/soccer/500/113.png",
    "MON": "https://a.espncdn.com/i/teamlogos/soccer/500/3282.png",
    "NAP": "https://a.espncdn.com/i/teamlogos/soccer/500/114.png",
    "PAR": "https://a.espncdn.com/i/teamlogos/soccer/500/115.png",
    "ROM": "https://a.espncdn.com/i/teamlogos/soccer/500/117.png",
    "TOR": "https://a.espncdn.com/i/teamlogos/soccer/500/239.png",
    "UDI": "https://a.espncdn.com/i/teamlogos/soccer/500/118.png",
    "VER": "https://a.espncdn.com/i/teamlogos/soccer/500/2180.png",
    "VEN": "https://a.espncdn.com/i/teamlogos/soccer/500/3283.png",
}


def clean_role(raw_role):
    r = str(raw_role).strip().upper()
    if r in ["P", "POR", "1"]:
        return "P"
    if r in ["D", "DIF", "2"]:
        return "D"
    if r in ["C", "CEN", "3"]:
        return "C"
    return "A"


def get_wikipedia_photo(player_name):
    """Cerca la foto su Wikipedia o restituisce vuoto se non trovata."""
    try:
        url = f"https://it.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(player_name)}&prop=pageimages&format=json&pithumbsize=200"
        headers = {"User-Agent": "FantaValueBot/1.0"}
        res = requests.get(url, headers=headers, timeout=1.2).json()
        pages = res.get("query", {}).get("pages", {})
        for _, val in pages.items():
            if "thumbnail" in val:
                return val["thumbnail"]["source"]
    except Exception:
        pass
    return ""


def update_database():
    print("🔄 Scaricamento dell'intero listone Serie A...")
    headers = {"User-Agent": "Mozilla/5.0"}

    players_db = []

    try:
        res = requests.get(DATA_URL, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            for p in data:
                nome = p.get("nome") or p.get("Nome") or p.get("name")
                if not nome:
                    continue

                squadra = str(
                    p.get("squadra") or p.get("Squadra") or "SER"
                )[:3].upper()
                ruolo = clean_role(p.get("ruolo") or p.get("R") or "A")
                pma = int(
                    p.get("qt") or p.get("Qt") or p.get("pma") or p.get("price") or 1
                )
                fm = float(
                    p.get("fm") or p.get("Fm") or p.get("fantamedia") or 6.0
                )
                tit = int(
                    p.get("tit") or p.get("Tit") or p.get("titolarita") or 75
                )

                # Gestione Foto: tenta la foto del calciatore, altrimenti stemma squadra
                foto_url = ""
                if pma >= 15:
                    foto_url = get_wikipedia_photo(str(nome).title())

                # Se non c'è la foto del giocatore, usa lo stemma ufficiale della squadra
                if not foto_url:
                    foto_url = TEAM_LOGOS.get(squadra, "")

                players_db.append({
                    "nome": str(nome).title(),
                    "squadra": squadra,
                    "ruolo": ruolo,
                    "fantamedia": fm,
                    "titolarita": tit,
                    "pma": pma,
                    "foto": foto_url,
                    "stemma": TEAM_LOGOS.get(squadra, ""),
                })
        else:
            print(f"❌ Errore risposta HTTP: {res.status_code}")
    except Exception as e:
        print(f"⚠️ Errore download dati: {e}")

    if not players_db:
        print("❌ Impossibile generare la lista. Annullamento.")
        return

    # Salva il file JSON con tutti i 500+ giocatori
    with open("players.json", "w", encoding="utf-8") as f:
        json.dump(players_db, f, ensure_ascii=False, indent=2)

    print(
        f"🎉 Ottimo! 'players.json' generato con successso: {len(players_db)} calciatori caricati con foto e stemmi."
    )


if __name__ == "__main__":
    update_database()
