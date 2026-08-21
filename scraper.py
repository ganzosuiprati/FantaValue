import json
import urllib.parse
import requests

# Feed pubblico ad alta affidabilità con oltre 500 calciatori
DATA_URL = "https://raw.githubusercontent.com/fede-co/fantacalcio-api/main/quotazioni.json"

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


def update_database():
    print("🔄 Download listone Serie A in corso...")
    headers = {"User-Agent": "Mozilla/5.0"}
    players_db = []

    try:
        res = requests.get(DATA_URL, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            for idx, p in enumerate(data):
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

                stemma = TEAM_LOGOS.get(squadra, "")

                players_db.append({
                    "id": p.get("id", idx + 1),
                    "nome": str(nome).title(),
                    "squadra": squadra,
                    "ruolo": ruolo,
                    "fantamedia": fm,
                    "titolarita": tit,
                    "pma": pma,
                    "foto": stemma,
                    "stemma": stemma,
                })
    except Exception as e:
        print(f"❌ Errore durante il download: {e}")

    if len(players_db) > 50:
        with open("players.json", "w", encoding="utf-8") as f:
            json.dump(players_db, f, ensure_ascii=False, indent=2)
        print(f"✅ 'players.json' salvato con {len(players_db)} calciatori!")
    else:
        print("⚠️ Dati insufficienti. Il file non è stato sovrascritto.")


if __name__ == "__main__":
    update_database()
