# PredictaMed — triaj predictiv geospațial (Prove It / Tremend)

Proiect dezvoltat în cadrul hackathonului **„Prove It”** (probă 24h, sponsor **Tremend / Publicis Sapient**). Aplicația combină prognoza meteo pe coordonatele spitalului, un model **Prophet** antrenat pe date istorice de admisii și vreme, evenimente majore din apropiere și un LLM (**Google Gemini**) pentru rapoarte text și scenarii „what-if”.

---

## Rezumat

**PredictaMed** este o aplicație **Streamlit** în care utilizatorul alege **orașul** și **unitatea medicală** din `data/spitale.csv` (cu latitudine/longitudine), apoi o **dată** în intervalul permis de UI (azi … +14 zile). La apăsarea **„Generează Raport de Risc”**, backend-ul:

1. Citește prognoza **Open-Meteo** pentru **cinci puncte** în jurul spitalului (centru + offset ~10 km N/S/E/V) și păstrează scenariul cu **cea mai mare deviație** față de media istorică a volumului de pacienți (estimare Prophet).
2. Interoghează **PredictHQ** pentru evenimente (festivaluri, sport, concerte) în raza configurată, relevante pentru intervalul ales.
3. Include **sărbători legale din România** în contextul trimis către model și în antrenament (componentă holidays în Prophet).
4. **Gemini** (`gemini-2.5-flash`, SDK `google.genai`) redactează un raport scurt pentru primiri urgențe (rezumat, influență meteo asupra tipului de cazuri, recomandări). În fila **„What-If Simulator”**, același lanț de date alimentează răspunsuri la întrebări/scenarii libere ale utilizatorului.

Predicția numerică este **agregată la nivel de flux de pacienți** (date de admisie zilnice), nu pe secții/departamente individuale în cod; interpretarea în limbaj natural rămâne la LLM, pe baza acelor indicatori.

---

## Problemă și abordare

Spitalele din zone diferite (munte, litoral, urban) au tipare de cerere influențate de vreme și de evenimente locale. Soluția propusă: **rutare geospațială la cerere** (coordonate din lista de spitale + API meteo + evenimente) și **explicare** prin LLM, astfel încât managerii să primească un mesaj lizibil, nu doar un scor brut.

---

## Funcționalități (implementate în repo)

| Zonă | Descriere |
|------|-----------|
| **Interfață** | Sidebar: oraș → listă spitale din CSV → dată → buton raport. Două file: raport de risc și simulator what-if. |
| **Date geospațiale** | `data/spitale.csv` (oraș, nume spital, `lat`, `long`). Există și `data/spitale_Romania.geojson` / `hospital_maker.py` pentru lucrul cu seturi geografice. |
| **Meteo** | `data/weather.py` — `api.open-meteo.com/v1/forecast` (zilnic: temperaturi, precipitații, zăpadă, umiditate, vânt, cod vreme). |
| **Evenimente** | `data/events.py` — API PredictHQ, filtrare geografică și după categorie/rank. |
| **ML** | `core/ai_engine.py` + `core/csv_parser.py`: îmbinare `admission_data.csv` / `admission_data_2.csv` cu `meteo.csv`; Prophet cu regresori meteo + `is_event_day`; model serializat în `core/prophet_model.json` (reantrenare la prima rulare dacă lipsește fișierul). |
| **LLM** | Doar **Gemini** (nu OpenAI în codul curent). Chei în `data/keys.py` (`Keys.AI_KEY`, `Keys.EVENT_API_KEY`). |

---

## Arhitectura datelor (pe scurt)

1. **Antrenament / încărcare model:** fuziune date admisii + meteo istoric → Prophet → predicție pentru ferestrele viitoare construite în `core/api_parser.py` din prognoza Open-Meteo și evenimente.
2. **La raport:** `process_coords` evaluează cele 5 zone, selectează predicția extremă, construiește `param_list` (dată, meteo, procent față de medie) + text evenimente/sărbători → prompt → `llm_process` / `what_if_process`.

---

