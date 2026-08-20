import json
import urllib.parse
import requests


def get_wikipedia_photo(player_name):
    """Recupera l'avatar da Wikipedia.

    Usa un try/except veloce per non rallentare lo script.
    """
    try:
        query = f"{player_name} calciatore"
        url = f"https://it.wikipedia.org/w/api.php?action=query&titles={urllib.parse.quote(query)}&prop=pageimages&format=json&pithumbsize=150"
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
        }
        res = requests.get(url, headers=headers, timeout=1.5).json()
        pages = res.get("query", {}).get("pages", {})
        for _, val in pages.items():
            if "thumbnail" in val:
                return val["thumbnail"]["source"]
    except Exception:
        pass
    return ""


def clean_role(raw_role):
    """Mappa i ruoli ufficiali Fantacalcio."""
    r = str(raw_role).strip().upper()
    if r in ["P", "POR", "1"]:
        return "P"
    if r in ["D", "DIF", "2"]:
        return "D"
    if r in ["C", "CEN", "3"]:
        return "C"
    return "A"


def update_database():
    print("🔄 Scaricamento listone completo Serie A in corso...")

    # Endpoint JSON pubblico con tutte le quotazioni ufficiali aggiornate
    url = "https://raw.githubusercontent.com/fede-co/fantacalcio-api/main/quotazioni.json"
    backup_url = "https://fantaservice.com/api/v1/players"

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0"
            " Safari/537.36"
        )
    }

    players_db = []

    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            for p in data:
                # Estrazione e pulizia campi
                nome = p.get("nome") or p.get("Nome") or "Sconosciuto"
                squadra = (
                    p.get("squadra") or p.get("Squadra") or "Serie A"
                ).upper()
                ruolo = clean_role(p.get("ruolo") or p.get("R") or "A")

                # Quotazione reale iniziale (Pma/Qt)
                pma = int(p.get("qt") or p.get("Qt") or p.get("pma") or 1)

                # Statistiche
                fm = float(p.get("fm") or p.get("Fm") or 6.0)
                tit = int(p.get("tit") or p.get("Tit") or 75)

                players_db.append({
                    "nome": nome.title(),
                    "squadra": squadra[:3],  # Tr Tronca a 3 lettere (es. INT, NAP, ROM)
                    "ruolo": ruolo,
                    "fantamedia": fm,
                    "titolarita": tit,
                    "pma": pma,
                    "foto": "",  # Le foto verranno caricate dinamicamente o per i top player
                })
        else:
            raise Exception(f"HTTP Error {res.status_code}")

    except Exception as e:
        print(f"⚠️ Impossibile scaricare dal primario ({e}), provo sorgente di riserva...")
        try:
            res_alt = requests.get(backup_url, headers=headers, timeout=10)
            data_alt = res_alt.json()
            for p in data_alt:
                players_db.append({
                    "nome": p.get("name", "Player").title(),
                    "squadra": p.get("team", "SER")[:3].upper(),
                    "ruolo": clean_role(p.get("role", "A")),
                    "fantamedia": float(p.get("avg", 6.0)),
                    "titolarita": int(p.get("starter_percent", 70)),
                    "pma": int(p.get("price", 1)),
                    "foto": "",
                })
        except Exception as err:
            print(f"❌ Errore fatale: {err}")

    # Aggiunta foto Wikipedia per i giocatori principali (evita di fare 500 chiamate di rete che bloccano il workflow)
    print("📸 Recupero avatar per i calciatori principali...")
    for player in players_db:
        if player["pma"] >= 15:  # Prende la foto solo per i giocatori con quotazione alta
            player["foto"] = get_wikipedia_photo(player["nome"])

    # Salva il file JSON
    with open("players.json", "w", encoding="utf-8") as f:
        json.dump(players_db, f, ensure_ascii=False, indent=2)

    print(f"✅ Completato! 'players.json' generato con {len(players_db)} giocatori reali.")


if __name__ == "__main__":
    update_database()
