import json
import random

# Struttura Dati Mock/Live per My FantaCola
data = {
    "giornata": 28,
    "news": [
        {"id": 1, "tipo": "RIENTRI", "titolo": "Rientro Lampo in Attacco", "testo": "Attaccante top torna ad allenarsi in gruppo: pronto a partire dal 1'."},
        {"id": 2, "tipo": "CONSIGLIATI", "titolo": "Scommesse di Giornata", "testo": "In centrocampo da schierare i tiratori da fuori per questa 28ª giornata."},
        {"id": 3, "tipo": "INFORTUNI", "titolo": "Tegola in Difesa", "testo": "Risentimento muscolare durante il riscaldamento: a rischio per la partita."}
    ],
    "partite": [
        {
            "match": "INTER vs JUVENTUS",
            "orario": "Sabato 20:45",
            "squadre": {
                "casa": {
                    "nome": "INTER",
                    "modulo_probabile": "3-5-2",
                    "titolari": ["Sommer", "Pavard", "Acerbi", "Bastoni", "Darmian", "Barella", "Calhanoglu", "Mkhitaryan", "Dimarco", "Thuram", "Lautaro"],
                    "ballottaggi": [
                        {"p1": "Darmian (60%)", "p2": "Dumfries (40%)"},
                        {"p1": "Mkhitaryan (55%)", "p2": "Frattesi (45%)"}
                    ],
                    "indisponibili": ["Arnautovic (Infortunato - Rientro g.30)"]
                },
                "trasferta": {
                    "nome": "JUVENTUS",
                    "modulo_probabile": "3-4-2-1",
                    "titolari": ["Di Gregorio", "Gatti", "Bremer", "Danilo", "Cambiaso", "Locatelli", "Thuram", "Kostic", "Yildiz", "Koopmeiners", "Vlahovic"],
                    "ballottaggi": [
                        {"p1": "Danilo (50%)", "p2": "Savona (50%)"}
                    ],
                    "indisponibili": ["Conceicao (Squalificato)"]
                }
            }
        }
    ],
    "consigliati_ruolo": {
        "P": ["Sommer", "Di Gregorio", "Maignan"],
        "D": ["Dimarco", "Bremer", "Theo Hernandez", "Buongiorno"],
        "C": ["Calhanoglu", "Barella", "Koopmeiners", "Pulisic"],
        "A": ["Lautaro", "Vlahovic", "Thuram", "Retegui"]
    }
}

with open("fantacola_data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("Database My FantaCola generato con successo!")
