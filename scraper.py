import json
import urllib.parse
import requests


def get_wikipedia_photo(player_name):
    """Recupera l'avatar da Wikipedia in modo sicuro."""
    try:
        query = f"{player_name} calciatore"
        url = f"https://it.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(query)}&prop=pageimages&format=json&pithumbsize=150"
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get(url, headers=headers, timeout=1.5).json()
        pages = res.get("query", {}).get("pages", {})
        for _, val in pages.items():
            if "thumbnail" in val:
                return val["thumbnail"]["source"]
    except Exception:
        pass
    return ""


def clean_role(raw_role):
    r = str(raw_role).strip().upper()
    if r in ["P", "POR", "1"]:
        return "P"
    if r in ["D", "DIF", "2"]:
        return "D"
    if r in ["C", "CEN", "3"]:
        return "C"
    return "A"


def fetch_from_sources():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
    }

    # Endpoint 1: API pubblica Fantagazzetta/Fantacalcio
    try:
        url = "https://raw.githubusercontent.com/luigi-s/fantacalcio-dataset/main/quotazioni.json"
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200 and len(res.json()) > 50:
            return [
                {
                    "nome": str(p.get("Nome", p.get("nome", ""))).title(),
                    "squadra": str(
                        p.get("Squadra", p.get("squadra", "SER"))
                    )[:3].upper(),
                    "ruolo": clean_role(p.get("R", p.get("ruolo", "A"))),
                    "fantamedia": float(p.get("Fm", p.get("fantamedia", 6.0))),
                    "titolarita": int(p.get("Tit", p.get("titolarita", 75))),
                    "pma": int(p.get("Qt", p.get("pma", 1))),
                    "foto": "",
                }
                for p in res.json()
            ]
    except Exception as e:
        print(f"⚠️ Query Fonte 1 fallita: {e}")

    # Endpoint 2: Fallback API di backup
    try:
        url_backup = "https://fantapazz.com/api/v1/players"
        res = requests.get(url_backup, headers=headers, timeout=5)
        if res.status_code == 200 and len(res.json()) > 50:
            return [
                {
                    "nome": str(p.get("name", "")).title(),
                    "squadra": str(p.get("team", "SER"))[:3].upper(),
                    "ruolo": clean_role(p.get("role", "A")),
                    "fantamedia": float(p.get("fm", 6.0)),
                    "titolarita": int(p.get("starter_rate", 70)),
                    "pma": int(p.get("price", 1)),
                    "foto": "",
                }
                for p in res.json()
            ]
    except Exception as e:
        print(f"⚠️ Query Fonte 2 fallita: {e}")

    return []


def update_database():
    print("🔄 Avvio recupero listone Serie A...")
    players_db = fetch_from_sources()

    # PROTEZIONE FONDAMENTALE: Se il fetch restituisce 0 giocatori, interrompe la sovrascrittura!
    if not players_db or len(players_db) < 50:
        print(
            "❌ ERRORE CRITICO: Impossibile scaricare i dati online. Il file 'players.json' NON verrà sovrascritto con un array vuoto."
        )
        # Forza l'uscita con codice d'errore per segnalare il fallimento su GitHub Actions
        exit(1)

    print(
        f"✅ Estratti {len(players_db)} calciatori! Caricamento foto Wikipedia..."
    )

    # Aggiunta foto per i top player (pma >= 15)
    for p in players_db:
        if p["pma"] >= 15:
            p["foto"] = get_wikipedia_photo(p["nome"])

    # Salvataggio sicuro nel JSON
    with open("players.json", "w", encoding="utf-8") as f:
        json.dump(players_db, f, ensure_ascii=False, indent=2)

    print("🎉 File 'players.json' aggiornato con successo!")


if __name__ == "__main__":
    update_database()
