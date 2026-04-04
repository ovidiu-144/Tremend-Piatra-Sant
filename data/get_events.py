import requests

api_key1 = "ZGAvkjKU7f1GfWaNLRgX9c_ISOYXKQ8UY0hlqaiv"


def get_romania_events(lat, lon, api_key, start_date="2026-04-01", end_date="2026-04-30"):
    url = "https://api.predicthq.com/v1/events/"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    params = {
        # 'within' combina distanta si punctul intr-un singur string validat
        "within": f"10km@{lat},{lon}", 
        "category": "festivals,sports,concerts",
        "active.gte": start_date,
        "active.lte": end_date,
        "rank.gte": 60,
        "phq_attendance.gte": 5000,
        "limit": 50
        # NOTA: Daca folosesti 'within', poti scoate 'country=RO' pentru a vedea 
        # daca filtrarea geografica devine prioritara.
    }
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        raw_results = response.json().get('results', [])
        clean_events = []

        for event in raw_results:
            # Extragem doar "esența" pentru modelul nostru de AI
            clean_event = {
                "titlu": event.get("title"),
                "categorie": event.get("category"),
                "data_start": event.get("start_local"),
                "estimare_participanti": event.get("phq_attendance", 0),
                "nivel_importanta": event.get("rank", 0),
                "locatie_nume": event.get("geo", {}).get("address", {}).get("formatted_address", "N/A"),
                # Adaugam etichete specifice (ex: 'rock', 'soccer') pentru contextul medical
                "tip_detaliat": [label['label'] for label in event.get('phq_labels', [])]
            }
            clean_events.append(clean_event)
        
        return clean_events
    else:
        print(f"Eroare: {response.status_code}, {response.text}")
        return None

#Testem pe Bucuresti

response = get_romania_events(44.4659572,26.0740855, api_key1, "2026-04-01", "2026-04-10")
print (response)