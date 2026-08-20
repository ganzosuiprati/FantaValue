import json
import urllib.parse
import requests

# Sorgente aperta raw GitHub (nessun blocco IP o Cloudflare)
PRIMARY_URL = "https://raw.githubusercontent.com/fede-co/fantacalcio-api/main/quotazioni.json"
BACKUP_URL = "https://raw.githubusercontent.com/luigi-s/fantacalcio-dataset/main/quotazioni.json"


def clean_role(raw_role):
    """Normalizza i ruoli nei quattro standard del Fantacalcio (P, D, C, A)."""
    r = str(raw_role).strip().upper()
    if r in ["P", "POR", "1"]:
        return "P"
    if r in ["D", "DIF", "2"]:
        return "D"
    if r in ["C", "CEN", "3"]:
        return "C"
    return "A"


def get_wikipedia_photo(player_name):
    """Recupera l'avatar da Wikipedia solo per i top player per velocizzare l'esecuzione."""
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


def fetch_data():
    headers = {"User-Agent": "Mozilla/5.0"}

    # Prova la prima sorgente
    try:
        res = requests.get(PRIMARY_URL, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if len(data) > 50:
                return data, "primary"
    except Exception as e:
        print(f"⚠️ Sorgente primaria fallita: {e}")

    # Prova la sorgente di riserva
    try:
        res = requests.get(BACKUP_URL, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if len(data) > 50:
                return data, "backup"
    except Exception as e:
        print(f"⚠️ Sorgente backup fallita: {e}")

    return None, None


def update_database():
    print("🔄 Avvio download listone Serie A...")
    raw_data, source_type = fetch_data()

    if not raw_data:
        print("❌ Impossibile scaricare i dati. Annullamento per proteggere il file locale.")
        exit(1)

    players_db = []

    for p in raw_data:
        # Pescaggio dinamico flessibile basato sulla struttura del JSON
        nome = p.get("nome") or p.get("Nome") or p.get("name")
        if not nome:
            continue

        squadra = str(p.get("squadra") or p.get("Squadra") or p.get("team") or "SER")[:3].upper()
        ruolo = clean_role(p.get("ruolo") or p.get("R") or p.get("role") or "A")
        pma = int(p.get("qt") or p.get("Qt") or p.get("pma") or p.get("price") or 1)
        fm = float(p.get("fm") or p.get("Fm") or p.get("fantamedia") or 6.0)
        tit = int(p.get("tit") or p.get("Tit") or p.get("titolarita") or 75)

        players_db.append({
            "nome": str(nome).title(),
            "squadra": squadra,
            "ruolo": ruolo,
            "fantamedia": fm,
            "titolarita": tit,
            "pma": pma,
            "foto": ""
        })

    print(f"✅ Processati {len(players_db)} calciatori da sorgente ({source_type}). Recupero avatar...")

    # Aggiunge la foto da Wikipedia ai top player (PMA >= 18)
    for player in players_db:
        if player["pma"] >= 18:
            player["foto"] = get_wikipedia_photo(player["nome"])

    # Salva e popola automaticamente il file players.json
    with open("players.json", "w", encoding="utf-8") as f:
        json.dump(players_db, f, ensure_ascii=False, indent=2)

    print("🎉 'players.json' aggiornato con successo!")


if __name__ == "__main__":
    update_database()
